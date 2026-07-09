"""
Round robin tournament runner for the ChessBot AIs.

Runs every configured AI against the others (white and black) so the
resulting rating matrix, summary CSV and Elo graph capture actual games.
"""

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from ai_players import (
    AdvancedAI,
    AlphaBetaAI,
    GreedyAI,
    MinimaxAI,
    NegamaxAI,
    RandomAI,
)
from chess_engine import ChessEngine

OUTPUT_DIR = Path("output")
ROUND_ROBIN_DIR = OUTPUT_DIR / "round_robin"
ROUND_ROBIN_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class AIConfig:
    """AI configuration (label plus constructor arguments)."""

    label: str
    ai_cls: Any
    init_kwargs: Dict[str, Any]


def build_ai_configs(advanced_test_mode: bool) -> List[AIConfig]:
    """Build a default AI configuration list (supporting AdvancedAI testing/game modes)."""
    advanced_depth = 7 if advanced_test_mode else 5
    mode_name = "Test" if advanced_test_mode else "Game"
    return [
        AIConfig("Random AI (Beginner)", RandomAI, {}),
        AIConfig("Greedy AI (Intermediate)", GreedyAI, {}),
        AIConfig("Minimax AI (Advanced-Depth 2)", MinimaxAI, {"depth": 2}),
        AIConfig("Alpha-Beta AI (Advanced-Depth 3)", AlphaBetaAI, {"depth": 3}),
        AIConfig("Negamax AI (Advanced-Depth 3)", NegamaxAI, {"depth": 3}),
        AIConfig(
            f"Advanced AI ({mode_name}-Depth {advanced_depth})",
            AdvancedAI,
            {"depth": advanced_depth, "test_mode": advanced_test_mode},
        ),
    ]


def instantiate_ai(config: AIConfig, color: bool):
    """Create AI instances of corresponding colors according to the configuration."""
    return config.ai_cls(color, **config.init_kwargs)


def play_game(
    white_config: AIConfig,
    black_config: AIConfig,
    max_moves: int,
) -> Tuple[str, int]:
    """Run a game of AI vs. AI without using a GUI and return the result and the number of moves."""
    white_ai = instantiate_ai(white_config, True)
    black_ai = instantiate_ai(black_config, False)
    engine = ChessEngine()
    move_count = 0

    while move_count < max_moves and not engine.is_game_over():
        current_ai = white_ai if engine.get_turn() else black_ai
        move = None
        try:
            move = current_ai.get_move(engine.board)
        except Exception:
            move = None

        if not move or move not in engine.board.legal_moves:
            legal_moves = list(engine.board.legal_moves)
            if not legal_moves:
                break
            move = random.choice(legal_moves)

        engine.make_move(move)
        move_count += 1

    result = engine.get_result()
    if result is None:
        if (
            engine.board.is_repetition(3)
            or engine.board.is_fifty_moves()
            or engine.board.is_insufficient_material()
        ):
            result = "draw"
        else:
            result = "draw"

    return result, move_count


def record_result(
    ordered_stats: Dict[Tuple[int, int], Dict[str, Any]],
    matches: List[Tuple[str, str, float]],
    total_points: Dict[str, float],
    games_played: Dict[str, int],
    white_idx: int,
    black_idx: int,
    result: str,
    moves: int,
    labels: List[str],
) -> None:
    """Record the impact of a game in the matrix, points, and match records."""
    entry = ordered_stats.setdefault(
        (white_idx, black_idx),
        {"white_wins": 0, "black_wins": 0, "draws": 0, "games": 0, "moves_sum": 0},
    )
    entry["games"] += 1
    entry["moves_sum"] += moves

    if result == "white":
        entry["white_wins"] += 1
        white_score = 1.0
    elif result == "black":
        entry["black_wins"] += 1
        white_score = 0.0
    else:
        entry["draws"] += 1
        white_score = 0.5

    white_label = labels[white_idx]
    black_label = labels[black_idx]
    matches.append((white_label, black_label, white_score))
    total_points[white_label] += white_score
    total_points[black_label] += 1.0 - white_score
    games_played[white_label] += 1
    games_played[black_label] += 1


def build_matrix(
    ordered_stats: Dict[Tuple[int, int], Dict[str, Any]],
    num_ai: int,
) -> np.ndarray:
    """Construct a white player's expected score matrix based on the recorded match results."""
    matrix = np.full((num_ai, num_ai), 0.5)
    for (white_idx, black_idx), entry in ordered_stats.items():
        if entry["games"] == 0:
            continue
        score = entry["white_wins"] + entry["draws"] * 0.5
        matrix[white_idx, black_idx] = score / entry["games"]
    return matrix


def build_summary(
    ordered_stats: Dict[Tuple[int, int], Dict[str, Any]],
    labels: List[str],
) -> List[Dict[str, Any]]:
    rows = []
    for (white_idx, black_idx), entry in ordered_stats.items():
        games = entry["games"]
        if games == 0:
            continue
        white_score = (entry["white_wins"] + entry["draws"] * 0.5) / games
        rows.append(
            {
                "White": labels[white_idx],
                "Black": labels[black_idx],
                "White Score": round(white_score, 3),
                "White Wins": entry["white_wins"],
                "Black Wins": entry["black_wins"],
                "Draws": entry["draws"],
                "Games": games,
                "Avg Moves": round(entry["moves_sum"] / games, 1),
            }
        )
    rows.sort(key=lambda item: (-item["White Score"], item["White"], item["Black"]))
    return rows


def run_round_robin(
    configs: List[AIConfig],
    games_per_pair: int,
    max_moves: int,
    verbose: bool = False,
) -> Tuple[
    np.ndarray,
    List[str],
    List[Dict[str, Any]],
    List[Tuple[str, str, float]],
    Dict[str, float],
    Dict[str, int],
]:
    labels = [cfg.label for cfg in configs]
    ordered_stats: Dict[Tuple[int, int], Dict[str, Any]] = {}
    matches: List[Tuple[str, str, float]] = []
    total_points = {label: 0.0 for label in labels}
    games_played = {label: 0 for label in labels}
    total_pairs = len(configs) * (len(configs) - 1) // 2
    total_games = total_pairs * games_per_pair
    game_counter = 0

    if verbose:
        print(f"A round-robin tournament with {total_games} rounds is about to start, involving {len(configs)} AIs.")

    progress_bar = tqdm(
        total=total_games,
        desc="Round Robin",
        unit="game",
        disable=verbose,
        ncols=100,
    )

    try:
        for white_base in range(len(configs)):
            for black_base in range(white_base + 1, len(configs)):
                for game_index in range(games_per_pair):
                    game_counter += 1
                    if game_index % 2 == 0:
                        white_idx, black_idx = white_base, black_base
                    else:
                        white_idx, black_idx = black_base, white_base

                    white_label = labels[white_idx]
                    black_label = labels[black_idx]
                    if verbose:
                        print(
                            f"[{game_counter}/{total_games}] "
                            f"{white_label} (white) vs {black_label} (black)"
                        )

                    result, moves = play_game(
                        configs[white_idx], configs[black_idx], max_moves
                    )
                    record_result(
                        ordered_stats,
                        matches,
                        total_points,
                        games_played,
                        white_idx,
                        black_idx,
                        result,
                        moves,
                        labels,
                    )
                    progress_bar.update(1)
    finally:
        progress_bar.close()

    matrix = build_matrix(ordered_stats, len(configs))
    summary = build_summary(ordered_stats, labels)
    return matrix, labels, summary, matches, total_points, games_played


def save_summary_csv(rows: List[Dict[str, Any]], path: Path):
    fieldnames = [
        "White",
        "Black",
        "White Score",
        "White Wins",
        "Black Wins",
        "Draws",
        "Games",
        "Avg Moves",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_matrix_csv(matrix: np.ndarray, labels: List[str], path: Path):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([""] + labels)
        for row_idx, label in enumerate(labels):
            row = [label] + [
                f"{matrix[row_idx, col_idx]:.3f}"
                for col_idx in range(matrix.shape[1])
            ]
            writer.writerow(row)


def plot_ratings(ratings: Dict[str, float], path: Path, title: str):
    labels = list(ratings.keys())
    values = [ratings[label] for label in labels]
    order = np.argsort(values)[::-1]
    labels = [labels[idx] for idx in order]
    values = [values[idx] for idx in order]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color="#4C72B0", alpha=0.9)
    plt.ylabel("Elo", fontsize=12)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 5,
            f"{value:.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.tight_layout()
    plt.savefig(path.as_posix(), dpi=220, bbox_inches="tight")
    plt.close()


def plot_rating_heatmap(matrix: np.ndarray, labels: List[str], path: Path, title: str):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(
        matrix,
        cmap="RdYlBu_r",
        vmin=0,
        vmax=1,
        aspect="auto",
        interpolation="nearest",
        origin="upper",
    )
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Black AI", fontsize=11, fontweight="bold")
    ax.set_ylabel("White AI", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)

    for i in range(len(labels)):
        for j in range(len(labels)):
            value = float(matrix[i, j])
            color = "white" if (value < 0.3 or value > 0.7) else "black"
            ax.text(j, i, f"{value:.3f}", ha="center", va="center", color=color, fontsize=8)

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("White Expected Score", fontsize=10, fontweight="bold")
    cbar.ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(path.as_posix(), dpi=220, bbox_inches="tight")
    plt.close(fig)


def estimate_elo_ratings(
    matches: List[Tuple[str, str, float]],
    labels: List[str],
    seed: int = None,
    k_factor: float = 24.0,
    iterations: int = 5,
) -> Dict[str, float]:
    ratings = {label: 1500.0 for label in labels}
    randomizer = random.Random(seed)

    for _ in range(iterations):
        shuffled = matches.copy()
        randomizer.shuffle(shuffled)
        for white_label, black_label, white_score in shuffled:
            expected = 1.0 / (1.0 + 10 ** ((ratings[black_label] - ratings[white_label]) / 400.0))
            delta = k_factor * (white_score - expected)
            ratings[white_label] += delta
            ratings[black_label] -= delta

    return ratings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a round-robin test for ChessBot AI, generate matrices, charts, and Elo rankings."
    )
    parser.add_argument(
        "--games-per-pair",
        "-g",
        type=int,
        default=2,
        help="The number of games played between each pair of AIs (taking turns to switch between white and black).",
    )
    parser.add_argument(
        "--max-moves",
        "-m",
        type=int,
        default=300,
        help="The maximum number of moves that can be made in a single game; if exceeded, the game is ruled a draw.",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--advanced-test",
        dest="mode",
        action="store_const",
        const="test",
        default="test",
        help="Use the test mode of AdvancedAI (depth 7, default behavior).",
    )
    mode_group.add_argument(
        "--game-mode",
        dest="mode",
        action="store_const",
        const="game",
        help="Use AdvancedAI's game mode (depth 5, quick response).",
    )
    parser.add_argument(
        "--include",
        "-i",
        nargs="+",
        help="Only include these AIs (case-insensitive, use the tags in --list or README).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the optional AI tags and exit.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for Elo estimation (used to control the shuffling order).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Output the progress line of each game.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    advanced_test = args.mode != "game"
    configs = build_ai_configs(advanced_test)

    if args.list:
        print("Optional AI:")
        for cfg in configs:
            print(f"- {cfg.label}")
        return

    if args.include:
        selected: List[AIConfig] = []
        lower_to_config = {cfg.label.lower(): cfg for cfg in configs}
        for label in args.include:
            match = lower_to_config.get(label.lower())
            if match is None:
                raise SystemExit(
                    f"Label '{label}' not found. Please use --list to view the available AI names."
                )
            if match not in selected:
                selected.append(match)
        configs = selected

    if len(configs) < 2:
        raise SystemExit("A round-robin tournament requires at least two different AIs.")

    if args.games_per_pair <= 0:
        raise SystemExit("--games-per-pair must be a positive integer.")

    matrix, labels, summary_rows, matches, total_points, games_played = run_round_robin(
        configs,
        args.games_per_pair,
        args.max_moves,
        verbose=args.verbose,
    )

    matrix_path = ROUND_ROBIN_DIR / "round_robin_matrix.csv"
    summary_path = ROUND_ROBIN_DIR / "round_robin_summary.csv"
    rating_chart_path = ROUND_ROBIN_DIR / "round_robin_ratings.png"
    heatmap_path = ROUND_ROBIN_DIR / "round_robin_heatmap.png"

    save_matrix_csv(matrix, labels, matrix_path)
    save_summary_csv(summary_rows, summary_path)
    elo_ratings = estimate_elo_ratings(matches, labels, seed=args.seed)
    plot_ratings(elo_ratings, rating_chart_path, "Round Robin Elo Ratings")
    plot_rating_heatmap(
        matrix, labels, heatmap_path, "Round Robin Expected Scores (White)"
    )

    print("\nRound-robin competition completed:")
    print(f"- Scoring matrix: {matrix_path}")
    print(f"- Detailed game summary: {summary_path}")
    print(f"- Elo bar chart: {rating_chart_path}")
    print(f"- Expected score heatmap: {heatmap_path}")
    print("\nElo ranking (based on actual games in a round-robin tournament):")
    for label, rating in sorted(elo_ratings.items(), key=lambda item: -item[1]):
        games = games_played[label]
        points = total_points[label]
        avg_points = points / games if games else 0.0
        print(
            f"  {label:30s}  Elo {rating:.0f}  | {points:.1f} points / {games} games "
            f"(averange {avg_points:.2f})"
        )


if __name__ == "__main__":
    main()

