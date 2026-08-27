# AI Chessbot

基于 Pygame 的国际象棋 AI 对战平台，实现多种搜索算法（Minimax、Alpha-Beta、Negamax、Advanced），支持人机对战、AI 对战与 Elo 评测。

## 这是什么

一个 Python 国际象棋 AI 项目，提供图形界面和六种不同强度的 AI 对手（从随机走子到高级搜索算法），可进行人机对战、AI 对战，并通过 Elo 评级系统评估 AI 强度。

## 特性

- **多种 AI 算法**：Random、Greedy、Minimax、Alpha-Beta、Negamax、Advanced（按强度递增）
- **Elo 评级系统**：预设 Elo 值（1421-1650+），可视化对比 AI 强度
- **双对战模式**：人机对战（H2M）和 AI 对战（M2M）
- **图形界面**：基于 Pygame 的现代 UI，支持走子、悔棋、保存战绩
- **AI 介绍界面**：查看所有 AI 的排名、Elo 评级和特性说明
- **战绩管理**：保存和查看历史对局记录（JSON 持久化）
- **AI 测试工具**：
  - `test_ai.py`：快速生成 Elo 评级图表和期望得分矩阵
  - `round_robin.py`：运行实际循环赛并生成真实对战数据

## 快速开始

### 安装依赖

```bash
git clone https://github.com/MIKE-He-525/ai-chessbot.git
cd ai-chessbot
pip install -r requirements.txt
```

### 运行游戏

```bash
python main.py
```

启动后进入主菜单，可选择：
- **Human vs AI**：人机对战，配置玩家颜色、AI 类型和难度
- **AI vs AI Battle**：AI 对战，配置双方 AI、难度、走子延迟和最大回合数
- **Bot Introduction**：查看所有 AI 的详细信息和排名
- **Score Records**：查看和清除历史战绩

## 使用

### 人机对战（H2M）

1. 主菜单选择 **Human vs AI**
2. 配置玩家颜色、AI 类型和难度（1-5）
3. 游戏中操作：
   - 鼠标点击移动棋子
   - 按 `U` 键悔棋（仅玩家回合）
   - 按 `ESC` 返回主菜单
   - 点击顶部按钮：返回菜单 / 重新开始 / 保存战绩

### AI 对战（M2M）

1. 主菜单选择 **AI vs AI Battle**
2. 配置白方/黑方 AI、难度、走子延迟和最大回合数
3. 游戏自动进行，支持将死、和棋、重复局面、50 回合规则等终局检测
4. 游戏结束后可保存战绩

### AI 强度测试

**快速生成图表**（使用预设 Elo 值）：

```bash
python test_ai.py
```

输出文件（保存在 `output/`）：
- `ai_ratings.png`：Elo 评级柱状图
- `rating_heatmap.png`：期望得分热力图（白方视角）
- `rating_matrix.csv`：期望得分矩阵

**实际循环赛测试**（真实对战数据）：

```bash
python round_robin.py --games-per-pair 2 --max-moves 300
```

常用参数：
- `--games-per-pair (-g)`：每对 AI 的对局数（默认 2，轮流执白/黑）
- `--max-moves (-m)`：单局最大回合数（默认 300）
- `--advanced-test`：启用 AdvancedAI 测试模式（深度 7，5 秒时间预算）
- `--game-mode`：切换到 AdvancedAI 游戏模式（深度 5，快速响应）
- `--include (-i)`：仅测试指定 AI（如 `--include random greedy minimax`）
- `--list`：列出所有可用 AI 标签
- `--verbose (-v)`：显示每局详细进度

输出文件（保存在 `output/round_robin/`）：
- `round_robin_matrix.csv`：实际得分矩阵
- `round_robin_summary.csv`：胜负统计和平均回合数
- `round_robin_ratings.png`：基于真实对战的 Elo 柱状图
- `round_robin_heatmap.png`：白方得分热力图

### AI 算法介绍

基于 Elo 评级系统的强度排名：

1. **Advanced AI**（Elo ~1650+）  
   双模式设计：游戏模式（深度 5，1.5 秒）用于流畅对战，测试模式（深度 7，5 秒）用于强度评估  
   特性：迭代加深、静态搜索、增强评估函数、置换表、优化走法排序

2. **Alpha-Beta AI**（Elo ~1572，深度 3）  
   经典博弈树搜索，支持 Alpha-Beta 剪枝和走法排序

3. **Minimax AI**（Elo ~1554，深度 2）  
   全宽度博弈树搜索，支持 Alpha-Beta 剪枝和置换表

4. **Negamax AI**（Elo ~1553，深度 3）  
   Minimax 的对称变体，代码更简洁，支持 Alpha-Beta 剪枝

5. **Random AI**（Elo ~1426）  
   随机走子，适合快速演示和基线测试

6. **Greedy AI**（Elo ~1421）  
   单步前瞻，贪婪选择当前最优走法，速度快但目光短浅

更多算法原理详见 `docs/algorithms.md`。

## 项目结构

```
ai-chessbot/
├── main.py                # 主程序（菜单、模式路由、界面）
├── ai_players.py          # AI 实现（Random、Greedy、Minimax、AlphaBeta、Negamax、Advanced）
├── chess_engine.py        # 游戏状态和规则引擎
├── chess_evaluation.py    # 评估函数和走法排序
├── chess_gui.py           # Pygame 图形界面
├── game_controller.py     # H2M/M2M 控制流和战绩逻辑
├── score_manager.py       # 战绩持久化
├── ui_components.py       # UI 组件（主题、按钮）
├── test_ai.py             # AI 强度测试（快速生成 Elo 图表）
├── round_robin.py         # AI 循环赛（真实对战数据）
├── requirements.txt       # Python 依赖列表
├── docs/algorithms.md     # 算法原理说明
└── output/                # 生成的图表和测试结果
```

## 依赖

- Python 3.8+（推荐 3.10/3.11）
- `pygame>=2.0.0`：图形界面
- `python-chess>=1.999`：国际象棋规则引擎
- `numpy>=1.20.0`：数值计算
- `pandas>=1.3.0`：数据处理
- `matplotlib>=3.3.0`：图表生成
- `tqdm>=4.65.0`：进度条显示

所有 AI 算法均为自主实现，不依赖外部 AI 库。
