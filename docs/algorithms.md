# Overview of Chess AI Algorithms

This article outlines the AI algorithms implemented in the project, their core ideas, optimization strategies, and applicable scenarios. Different algorithms strike a balance between "search quality vs. response speed," facilitating a balance between teaching, demonstration, and gameplay experience.

**Algorithm Strength Ranking** (based on the latest test results using the Elo rating system):
1. Advanced AI (depth 7) - Elo: ~1650+ (strongest)
2. Alpha-Beta AI (depth 3) - Elo: ~1572
3. Minimax AI (depth 2) - Elo: ~1554
4. Negamax AI (depth 3) - Elo: ~1553
5. Random AI - Elo: ~1426
6. Greedy AI - Elo: ~1421

> **Note**: Elo ratings are derived from round-robin test results, fitted using an expected score matrix. Higher ratings indicate stronger performance. Advanced AI, with in-depth optimizations, is significantly stronger than other algorithms.

---

## Alpha-Beta AI 

- **Elo Rating**: ~1572
- **Principle**: A classic game search algorithm combined with Alpha-Beta pruning optimization.
- **Implemented Optimizations**:
  - Alpha-Beta Pruning: Prunes branches immediately when they cannot affect the decision, reducing complexity from `O(b^d)` to approximately `O(b^(d/2))` with good ordering.
  - Move Ordering: Prioritizes captures/checks to improve pruning hit rate.
  - Uses `push/pop` instead of copying to reduce time complexity.
- **Applicable**: Depth 3-4, balancing speed and quality.
- **Limitations**: Complexity still explodes exponentially with increased depth; evaluation function is heuristic.

---

## Minimax AI

- **Elo Rating**: ~1554
- **Principle**: Full-width game tree search, alternating between maximizing for the current side and minimizing for the opponent.
- **Implemented Optimizations**:
  - Alpha-Beta Pruning: Prunes branches immediately when they cannot affect the decision, reducing complexity from `O(b^d)` to approximately `O(b^(d/2))` with good ordering.
  - Move Ordering: Prioritizes captures/checks to improve pruning hit rate.
  - Transposition Table (TT): Caches `(depth, score)` with FEN as the key to reuse repeated position evaluations.
  - Uses `push/pop` instead of copying to reduce time complexity.
- **Applicable**: Depth 2-4, balancing speed and quality.
- **Limitations**: Complexity still explodes exponentially with increased depth; evaluation function is heuristic.

---

## Negamax AI 

- **Elo Rating**: ~1553
- **Principle**: An equivalent variant of Minimax: `score(pos, color) = -score(next, -color)`, simplifying implementation with symmetric recursion.
- **Implemented Optimizations**:
  - Alpha-Beta pruning and move ordering, equivalent in strength to Alpha-Beta.
  - Fixed evaluation function to ensure perspective consistency (always returns score from White's perspective).
  - Uses `push/pop` instead of copying to reduce time complexity.
- **Features**: Cleaner code and more elegant implementation.
- **Applicable**: Depth 3-4, comparable in strength to Alpha-Beta.

---

## Advanced AI (Master-level, strongest)

- **Elo Rating**: ~1650+ (currently strongest)
- **Default Depth**: 7 (configurable, minimum 5)
- AdvancedAI is the most optimized and strongest AI, incorporating deep search, advanced evaluation, and various optimization strategies based on the Alpha-Beta framework:

### Core Features

#### 1. Deep Search and Optimization
- **Depth 7 Alpha-Beta Search**: Full-width search (no beam search restrictions) to ensure no critical variations are missed.
- **Quiescence Search**: Continues searching captures and checks when depth reaches 0 to avoid the "horizon effect".
- **Iterative Deepening**: Searches layer by layer from shallow to deep to find the optimal solution within the time budget.
- **Transposition Table (100,000 entries)**: Depth-aware caching to significantly reduce redundant calculations.

#### 2. Advanced Move Ordering
- **History Heuristic**: Records good moves to improve ordering quality.
- **Killer Heuristic**: Records moves that caused pruning at specific depths.
- **MVV-LVA (Most Valuable Victim - Least Valuable Attacker)**: Optimizes capture ordering.
- **Null Window Search (Principal Variation Search)**: Optimizes move ordering and improves pruning efficiency.

#### 3. Enhanced Evaluation Function
- **Enhanced Traditional Evaluation**:
  - Basic Evaluation: Uses common evaluation functions (piece values, mobility, check penalties).
  - Position Evaluation: Center control, extended center, pawn advancement rewards.
  - Mobility Evaluation: Precisely calculates the difference in the number of moves for both sides.
  - King Safety: Evaluation of the king's position in the middle game.
  - Castling Rights: Evaluates the value of castling.
  - Piece Advantage: Evaluation of piece values in the endgame.

#### 4. Engineering Optimizations (Reducing Interaction Latency)
- **Shared Caching**:
  - All AdvancedAI instances within the same process share the transposition table, history table, and killer table to avoid redundant calculations.
- **Time Budget (default 800ms, adjustable)**:
  - Searches iteratively within the time slice and can return the "current best solution" at any time.
  - Timeout Check: Periodically checks during recursion and returns static evaluation after timeout.
- **Full-Width Search**:
  - Removed beam search restrictions for full-width search to achieve optimal performance.

### Performance Characteristics
- **Search Depth**: Default 7 layers (compared to 2-4 layers for other AIs).
- **Time Budget**: 800ms (compared to 250ms for older versions).
- **Evaluation Quality**: Enhanced traditional evaluation function with multi-dimensional assessments including position, mobility, and king safety.
- **Search Efficiency**: Optimizations such as MTD-f algorithm, null move pruning, history heuristic, killer heuristic, and PVS significantly improve search efficiency.

> **Practical Effect**: Each move is strictly controlled by the time budget during the game, usually returning high-quality moves within 800ms. Its strength far exceeds other AIs, making it suitable as the strongest opponent.

---

## Random AI (Beginner)

- **Elo Rating**: ~1426
- **Idea**: Randomly selects from all legal moves with equal probability.
- **Goal**: Serves as the most basic baseline and debugging opponent, suitable for beginners to practice.
- **Features**: Almost almost no computational or evaluation overhead, no strategy.

---

## Greedy AI (Intermediate)

- **Elo Rating**: ~1421 (currently weakest)
- **Idea**: One-ply lookahead.
- **Process**:
  1. For each legal move, execute it temporarily.
  2. Score using a piece-based evaluation (with light mobility/check adjustments).
  3. White takes the maximum, Black takes the minimum move.
- **Advantages**: Extremely fast, good at seizing immediate piece gains.
- **Limitations**: Short-sighted, ignores opponent counterattacks and long-term structure, easily falls into simple traps.

---

## Comparison Table (Summary)

| Algorithm   | Elo Rating | Typical Depth | Pruning | Transposition Table | Evaluation Method                  | Applicable Scenarios       |
|-------------|-----------:|--------------:|---------|---------------------|-------------------------------------|----------------------------|
| Advanced    | ~1650+     | 7             | ✓       | ✓(shared)           | NN/enhanced traditional + quiescence search + heuristics | Strongest strength, master-level |
| Alpha-Beta  | ~1572      | 3–4           | ✓       | (optional)          | Piece-based (with light heuristics) | Strong strength, classic algorithm |
| Minimax     | ~1554      | 2–4           | ✓       | ✓                   | Piece-based (with light heuristics) | Balance of speed and quality |
| Negamax     | ~1553      | 3–4           | ✓       | (optional)          | Piece-based (with light heuristics) | Symmetric implementation, concise |
| Random      | ~1426      | 0             | ✗       | ✗                   | None                                | Baseline/demonstration      |
| Greedy      | ~1421      | 1             | ✗       | ✗                   | Piece-based (with light heuristics) | Quick testing              |

---

## Key Algorithm Points

### Minimax + Alpha-Beta (Pseudocode)
```
function minimax(node, depth, α, β, maximizing):
    if depth == 0 or node is terminal:
        return evaluate(node)
    moves = sort_moves(node.legal_moves)  # Prioritize captures/checks
    if maximizing:
        value = -∞
        for move in moves:
            node.push(move)
            value = max(value, minimax(node, depth-1, α, β, False))
            node.pop()
            α = max(α, value)
            if α >= β: break
        store_TT(node, depth, value)
        return value
    else:
        value = +∞
        for move in moves:
            node.push(move)
            value = min(value, minimax(node, depth-1, α, β, True))
            node.pop()
            β = min(β, value)
            if β <= α: break
        store_TT(node, depth, value)
        return value
```

Complexity: Without pruning `O(b^d)`; with good ordering, Alpha-Beta approximates `O(b^(d/2))`. Transposition tables can amortize repeated subtrees.

### Greedy (One-ply Lookahead)
```
best = -∞ (white) / +∞ (black)
for move in legal_moves:
    push(move); score = evaluate(board); pop()
    update best/best_move
return best_move
```
Complexity: `O(b)` (evaluates each legal move once).

### Negamax (with Alpha-Beta)
```
function negamax(node, depth, α, β, color):
    if depth == 0 or node terminal:
        return color * evaluate(node)
    moves = sort_moves(node.legal_moves)
    value = -∞
    for move in moves:
        node.push(move)
        score = -negamax(node, depth-1, -β, -α, -color)
        node.pop()
        value = max(value, score)
        α = max(α, value)
        if α >= β: break
    return value
```

---

## Evaluation Function Points

### Traditional Evaluation (for all non-NN modes)
- **Piece Weights**: Standard piece values (pawn=100, knight=320, bishop=330, rook=500, queen=900, king=20000)
- **Position Rewards**: Center control, extended center, pawn advancement rewards
- **Mobility**: Difference in the number of legal moves (precisely calculates move counts for both sides)
- **King Safety**: Check penalties, evaluation of the king's position in the middle game
- **Castling Rights**: Evaluates the value of castling
- **Capture Ordering**: MVV-LVA (Most Valuable Victim - Least Valuable Attacker)

### Advanced AI Enhanced Evaluation
- **Enhanced Traditional Evaluation**:
  - Basic Evaluation: Uses common evaluation functions (pieces, mobility, check penalties)
  - Position Evaluation: Center control, extended center, pawn advancement (forward progress rewards)
  - Mobility Evaluation: Precisely calculates the difference in the number of moves for both sides
  - King Safety: King is better positioned in the back during the middle game
  - Castling Rights: Evaluates the value of castling
  - Piece Advantage: Evaluation of piece values in the endgame

---

## Related Files
- `ai_players.py`: Classes and implementations of each AI (AdvancedAI's MTD-f algorithm, null move pruning, deep search, quiescence search, history/killer heuristics, time budget, shared caching, etc.).
- `chess_evaluation.py`: Common evaluation function utility module (extracts common evaluation logic).
- `chess_engine.py`: Position representation, rules, and basic evaluation support.
- `round_robin.py`: Test tool that runs actual round-robin tournaments (swapping White/Black) and generates score matrices, summary CSVs, and Elo visualization charts.

---
