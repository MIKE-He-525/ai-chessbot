# ChessBot - Chess AI Project

A Python-based chess AI project featuring a modern Pygame graphical interface, multiple AI algorithms (Random/Greedy/Minimax/Alpha-Beta/Negamax/Advanced), game score persistence, and AI strength testing (with visualization charts). AdvancedAI utilizes state-of-the-art search techniques (iterative deepening, quiescence search, etc.) and an enhanced traditional evaluation function.

## Features
- Graphical Interface (Pygame): Main menu, H2M (Human vs AI), M2M (AI vs AI) modes with fixed window layout and non-overlapping elements.
- Multiple AI Algorithms (sorted by strength):
  - Advanced AI: The strongest AI with deep search + advanced evaluation (Elo ~1650+)
  - Alpha-Beta AI: Classic game tree search (Elo ~1572)
  - Minimax AI: Full-width game tree search with Alpha-Beta pruning and transposition tables (Elo ~1554)
  - Negamax AI: Symmetric variant implementation of Minimax (Elo ~1553)
  - Random AI: Random legal moves (Elo ~1426)
  - Greedy AI: Greedily selects immediate optimal moves (Elo ~1421)
- AI Introduction Feature: The main menu provides a Bot Introduction interface showing all AI algorithms' rankings, Elo ratings, descriptions, and features.
- Game Score Management: Supports saving/viewing/clearing historical scores (JSON persistence).
- AI Strength Testing: Generate Elo rating charts and expected score matrices via `test_ai.py`, with unified output to `output/`.

## Requirements
- Python 3.8+ (3.10/3.11 recommended)
- Windows / macOS / Linux

## Dependencies
The project depends on the following Python packages (see `requirements.txt` for details):
- `pygame>=2.0.0`: Graphical interface
- `python-chess>=1.999`: Chess rule engine
- `numpy>=1.20.0`: Numerical calculations
- `pandas>=1.3.0`: Data processing
- `matplotlib>=3.3.0`: Chart generation
- `tqdm>=4.65.0`: Progress bar display

All AI algorithms are self-implemented and do not rely on external AI libraries.

## Installation
```bash
pip install -r requirements.txt
```

## Running
Start the main program:
```bash
python main.py
```

## Usage Instructions (integrated from USAGE.md)
### Quick Start
1) Install dependencies: `pip install -r requirements.txt`
2) Run the main program: `python main.py`

### Mode Explanations
- H2M (Human vs AI)
  1. Click "Human vs AI" in the main menu
  2. Select player color, AI type, and difficulty
  3. In-game support:
     - Mouse click to move pieces
     - Top bar: Back to Menu / Restart / Save Score
     - U key to undo last move (only during player's turn)
     - ESC to return to main menu

- M2M (AI vs AI Battle)
  1. Click "AI vs AI Battle" in the main menu
  2. Configure white/black AI types, difficulties, move delay, and maximum number of turns
  3. In-game also supports Back / Restart / Save Score (enabled after game ends)
  4. Automatic game end detection: checkmate, stalemate, repeated positions, 50-move rule, insufficient material, etc.

- Bot Introduction
  1. Click "Bot Introduction" in the main menu
  2. View detailed information about all AI algorithms:
     - Rankings and Elo ratings
     - Algorithm descriptions
     - Main features
  3. Displayed in order of strength from highest to lowest

### AI Strength Testing (test_ai.py)
Directly use preset Elo ratings to generate charts and expected score matrices:
```bash
python test_ai.py
```

**Feature Description**:
- No longer performs time-consuming round-robin tests
- Directly uses preset Elo rating values
- Calculates expected score matrix based on Elo formula
- Automatically generates visual charts

**Output Files**:
- `output/ai_ratings.png`: Elo rating bar chart
- `output/rating_heatmap.png`: Expected score heatmap (from white's perspective)
- `output/rating_matrix.csv`: Expected score matrix (CSV format)

**Preset Elo Ratings**:

### AI Round-Robin Testing (round_robin.py)
For real match data, run `round_robin.py` to have each pair of AIs play against each other as white/black, then generate rating matrices, Elo bar charts, and heatmaps based on actual results. The default configuration includes Random, Greedy, Minimax d2, Alpha-Beta d3, Negamax d3, and Advanced AI (test mode, depth 7). For a faster version with approximate game experience, use `--game-mode` to switch to depth 5.

```bash
python round_robin.py --games-per-pair 2 --max-moves 300
```

**Common Parameters**:
- `--games-per-pair (-g)`: Number of games per pair (taking turns as white/black), default 2.
- `--max-moves (-m)`: Maximum moves per game, automatically drawn if exceeded, default 300.
- `--advanced-test`: Enables AdvancedAI's test mode by default (depth 7, time budget 5 seconds).
- `--game-mode`: Switches to AdvancedAI's game mode (depth 5, fast response) to save time.
- `--include (-i)`: Test only specified AIs (case-insensitive, use `--list` to check correct labels).
- `--list`: Print available AI labels and exit.
- `--seed`: Set random seed for Elo estimation (maintains fixed order across multiple shuffles).
- `--verbose (-v)`: Print real-time progress for each game.

**Execution Feedback**:
- Uses `tqdm` progress bar to show completed games by default (switches to per-game output in `--verbose` mode, automatically disabling the progress bar).

**Output Files (unified in `output/round_robin/`)**:
- `round_robin_matrix.csv`: Actual score matrix when each AI plays as white.
- `round_robin_summary.csv`: Statistics like wins/losses and average moves for each white/black combination.
- `round_robin_ratings.png`: Elo bar chart based on real results.
- `round_robin_heatmap.png`: White's score heatmap (0-1).

**Note**: This script uses real game results to calculate expected scores and Elo, suitable for regression testing or evaluating AI after adjustments. However, it takes longer to run than `test_ai.py` due to actual gameplay, especially in `--advanced-test` mode.

### Score Records
1. Click "Save Score" at the top after game ends to save (button auto-disables after saving)
2. Click "Score Records" in main menu to view history
3. Click "Clear Records" to delete saved scores

### FAQ
- **Game running slowly?** AdvancedAI has a dual-mode design:
  - Game mode: Fast response (depth 5, 1.5s time budget) for smooth gameplay
  - Test mode: Full performance (depth 7, 5s time budget) for AI strength testing
  If still slow, reduce difficulty or choose simpler AI
- **M2M games stuck in loops?** Fixed, now automatically detects all game end conditions (repeated positions, 50-move rule, etc.)
- **How to exit?** Use ESC or close the window
- **How to view AI info?** Click "Bot Introduction" in main menu for detailed introductions
- **Interface issues?** Ensure dependencies are installed, especially pygame
- **Slow test scripts?** Use `--workers` parameter to enable multi-process parallelism for significant speedup (recommend setting to CPU core count)

## AI Algorithm Introduction (sorted by strength)

Based on latest test results (using expected score and Elo rating system), algorithm strength rankings are as follows:

1. **Advanced AI (depth 7)** - Elo: ~1650+
   - **Strongest AI**: Uses state-of-the-art search techniques and advanced evaluation strategies
   - **Dual-mode design**:
     * **Game mode** (test_mode=False): Fast response, depth 5, 1.5s time budget for smooth gameplay
     * **Test mode** (test_mode=True): Full performance, depth 7, 5s time budget for AI strength testing
   - **Iterative deepening**: Searches progressively from shallow to deep, finding optimal solutions within time budget
   - **Quiescence Search**: Continues searching captures and checks when depth reaches 0 to avoid horizon effect
   - **Optimized move ordering**: Prioritizes captures/checks to improve pruning efficiency
   - **Enhanced evaluation function**: Advanced features like position evaluation, mobility assessment, king safety evaluation
   - **Transposition table**: Caches searched position results to speed up repeated position searches

2. **Alpha-Beta AI (depth 3)** - Elo: ~1572
   - Classic game tree search algorithm with Alpha-Beta pruning optimization
   - Uses fast evaluation and move ordering (captures/checks first)
   - Uses `push/pop` instead of copying to reduce time complexity

3. **Minimax AI (depth 2)** - Elo: ~1554
   - Full-width game tree search with Alpha-Beta pruning and transposition tables
   - Uses fast evaluation and move ordering (captures/checks first)
   - Uses `push/pop` instead of copying to reduce time complexity

4. **Negamax AI (depth 3)** - Elo: ~1553
   - Symmetric variant implementation of Minimax with more concise code
   - Also incorporates Alpha-Beta pruning and move ordering
   - Evaluation function fixed to ensure perspective consistency

5. **Random AI** - Elo: ~1426
   - Randomly selects legal moves, suitable for quick demonstrations and baseline testing

6. **Greedy AI** - Elo: ~1421
   - Greedy selection based on simplified evaluation, fast but short-sighted
   - One-step lookahead, good at capturing immediate material gains

> **Note**: Elo ratings are derived from round-robin test results, fitted using expected score matrices. Higher ratings indicate stronger performance.

For more algorithm principles, refer to `docs/algorithms.md`.


## Directory Structure (core)
```
ChessBot/
├── main.py                 # Main program (menu/mode/interface routing)
├── chess_engine.py         # Game state and rules
├── chess_gui.py            # Pygame graphical interface
├── game_controller.py      # H2M/M2M control flow and scoring logic
├── ai_players.py           # Various AI implementations (including AdvancedAI)
├── chess_evaluation.py     # Common evaluation function utility module
├── score_manager.py        # Score persistence
├── test_ai.py              # AI strength testing (directly returns Elo values and generates charts)
├── round_robin.py          # AI round-robin testing (generates matrices and charts from real games)
├── ui_components.py        # UI components (themes, buttons, etc.)
├── requirements.txt        # Python dependency list
├── docs/algorithms.md      # Algorithm principle explanations
└── output/                 # Generated charts and test results (added to .gitignore)
```

## Technical Features

### AdvancedAI Core Technologies
- **Dual-mode design**:
  - **Game mode**: Fast response (depth 5, 1.5s time budget) for smooth gameplay
  - **Test mode**: Full performance (depth 7, 5s time budget) for AI strength testing
- **Iterative deepening**: Searches progressively from shallow to deep, finding optimal solutions within time budget
- **Quiescence search**: Continues searching captures and checks at depth 0 to avoid "horizon effect"
- **Optimized move ordering**: Prioritizes captures/checks to improve pruning efficiency
- **Enhanced evaluation**: Multi-dimensional assessment including position value, mobility, king safety
- **Transposition table**: Caches searched position results to speed up repeated position searches

### Game Engine Features
- **Complete rule support**: python-chess library provides full chess rules
- **Game end detection**: Automatically detects checkmate, stalemate, repeated positions, 50-move rule, insufficient material, etc.
- **M2M mode optimization**: Prevents infinite loops and ensures normal game termination

### Code Architecture
- **Common evaluation functions**: `chess_evaluation.py` provides unified evaluation and move ordering logic to reduce code duplication
- **Self-implemented**: All AI algorithms are self-developed without relying on external AI libraries (e.g., easyAI)
- **Modular design**: Clear module division for easy maintenance and extension

## Frequently Asked Questions
1. **Charts not generated**: Run `python test_ai.py` to generate charts, which are saved in the `output/` directory.
2. **Interface abnormalities**: Ensure dependencies are installed, especially pygame.
3. **M2M game issues**: Loop problems have been fixed, now correctly detecting all game end conditions.
4. **Abnormal test results**: Ensure using the latest version of test scripts, which include complete game end detection.
