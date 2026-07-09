"""
AI test script - directly return Elo values and generate charts
No longer conduct round-robin tournaments, directly use preset Elo values
"""
import csv
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np

from ai_players import RandomAI, GreedyAI, MinimaxAI, AlphaBetaAI, NegamaxAI, AdvancedAI

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# AI配置和预设Elo值
AI_CONFIGS = [
    ("Random", RandomAI, 0, 1426),
    ("Greedy", GreedyAI, 0, 1421),
    ("Minimax d2", MinimaxAI, 2, 1554),
    ("AlphaBeta d3", AlphaBetaAI, 3, 1572),
    ("Negamax d3", NegamaxAI, 3, 1553),
    ("Advanced d7", AdvancedAI, 7, 1650),
]

def get_elo_ratings() -> Dict[str, float]:
    return {label: elo for label, _, _, elo in AI_CONFIGS}

def calculate_expected_score_matrix(ratings: Dict[str, float]) -> np.ndarray:
    """
    Calculate the expected score matrix based on Elo ratings
    Use the Elo formula: E_A = 1 / (1 + 10^((R_B - R_A) / 400))
    """
    labels = list(ratings.keys())
    n = len(labels)
    matrix = np.zeros((n, n))
    
    for i, label_i in enumerate(labels):
        for j, label_j in enumerate(labels):
            if i == j:
                matrix[i, j] = 0.5
            else:
                rating_i = ratings[label_i]
                rating_j = ratings[label_j]
                expected = 1.0 / (1.0 + 10 ** ((rating_j - rating_i) / 400.0))
                matrix[i, j] = expected
    
    return matrix, labels

def save_rating_matrix(matrix: np.ndarray, labels: List[str], path: Path):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([""] + labels)
        for i, label in enumerate(labels):
            row = [label] + [f"{matrix[i, j]:.3f}" for j in range(len(labels))]
            writer.writerow(row)
    print(f"[Saved] {path}")

def plot_ratings(ratings: Dict[str, float], save_path: Path) -> None:
    labels = list(ratings.keys())
    values = [ratings[k] for k in labels]
    order = np.argsort(values)[::-1]
    labels = [labels[i] for i in order]
    values = [values[i] for i in order]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color="#4C72B0", alpha=0.9)
    plt.ylabel("Elo", fontsize=12)
    plt.title("AI Ratings (Elo)", fontsize=14, fontweight="bold")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y", alpha=0.25)
    for b, v in zip(bars, values):
        plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 5, 
                f"{v:.0f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path.as_posix(), dpi=220, bbox_inches="tight")
    plt.close()
    print(f"[Saved] {save_path}")

def plot_rating_heatmap(matrix: np.ndarray, labels: List[str], save_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, cmap="RdYlBu_r", vmin=0, vmax=1, aspect="auto", 
                   interpolation="nearest", origin="upper")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Black AI", fontsize=11, fontweight="bold")
    ax.set_ylabel("White AI", fontsize=11, fontweight="bold")
    ax.set_title("White Expected Score (0–1)", fontsize=14, fontweight="bold", pad=12)
    
    for i in range(len(labels)):
        for j in range(len(labels)):
            v = float(matrix[i, j])
            color = "white" if (v < 0.3 or v > 0.7) else "black"
            ax.text(j, i, f"{v:.3f}", ha="center", va="center", color=color, fontsize=8)
    
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("White Expected Score", fontsize=10, fontweight="bold")
    cbar.ax.tick_params(labelsize=8)
    fig.tight_layout()
    plt.savefig(save_path.as_posix(), dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"[Saved] {save_path}")

def main():
    print("=" * 60)
    print("AI Test Script - Directly return Elo value and generate charts")
    print("=" * 60)
    
    ratings = get_elo_ratings()
    
    matrix, labels = calculate_expected_score_matrix(ratings)
    
    save_rating_matrix(matrix, labels, OUTPUT_DIR / "rating_matrix.csv")
    
    plot_ratings(ratings, OUTPUT_DIR / "ai_ratings.png")
    plot_rating_heatmap(matrix, labels, OUTPUT_DIR / "rating_heatmap.png")
    
    print("\nElo Ratings (from high to low):")
    for k, v in sorted(ratings.items(), key=lambda x: -x[1]):
        print(f"  {k:15s} : {v:.0f}")
    
    print("\nCompleted!")
    print(f"Output file:")
    print(f"  - {OUTPUT_DIR / 'rating_matrix.csv'}")
    print(f"  - {OUTPUT_DIR / 'ai_ratings.png'}")
    print(f"  - {OUTPUT_DIR / 'rating_heatmap.png'}")

if __name__ == "__main__":
    main()

