from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.maze import Maze
from src.solvers import SolveResult, solve_maze


class MazeApp(tk.Tk):
    CELL_SIZE = 28
    PADDING = 18
    VISIT_DELAY_MS = 15
    STATUS_BOX_WIDTH = 230
    STATUS_BOX_HEIGHT = 120
    MOVE_MAP = {
        "Up": ("N", (0, -1)),
        "Down": ("S", (0, 1)),
        "Left": ("W", (-1, 0)),
        "Right": ("E", (1, 0)),
        "w": ("N", (0, -1)),
        "W": ("N", (0, -1)),
        "s": ("S", (0, 1)),
        "S": ("S", (0, 1)),
        "a": ("W", (-1, 0)),
        "A": ("W", (-1, 0)),
        "d": ("E", (1, 0)),
        "D": ("E", (1, 0)),
    }

    def __init__(self) -> None:
        super().__init__()
        self.title("MazeSolver 迷宫求解器")
        self.configure(bg="#f6f4ed")
        self.resizable(False, False)

        self.width_var = tk.IntVar(value=14)
        self.height_var = tk.IntVar(value=14)
        self.status_var = tk.StringVar(
            value="方向键或 WASD 可控制角色移动；你既可以自己闯关，也可以点击按钮查看 DFS、BFS、A* 的求解结果。"
        )

        self.maze = Maze(self.width_var.get(), self.height_var.get())
        self.current_result: SolveResult | None = None
        self.player_position = self.maze.start
        self.player_path = [self.maze.start]
        self.game_won = False

        self._build_layout()
        self._bind_controls()
        self._draw_maze()

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Panel.TFrame", background="#fffdf7")
        style.configure("Panel.TLabel", background="#fffdf7", foreground="#263238")
        style.configure("Panel.TButton", padding=6)

        control_panel = ttk.Frame(container, style="Panel.TFrame", padding=14)
        control_panel.grid(row=0, column=0, sticky="ns", padx=(0, 12))
        control_panel.grid_columnconfigure(0, weight=1)
        control_panel.grid_columnconfigure(1, weight=1)

        ttk.Label(
            control_panel,
            text="MazeSolver 迷宫求解器",
            style="Panel.TLabel",
            font=("Helvetica", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(
            control_panel,
            text="迷宫宽度",
            style="Panel.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(14, 2))
        ttk.Spinbox(
            control_panel,
            from_=8,
            to=28,
            textvariable=self.width_var,
            width=8,
        ).grid(row=1, column=1, sticky="ew", pady=(14, 2))

        ttk.Label(
            control_panel,
            text="迷宫高度",
            style="Panel.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Spinbox(
            control_panel,
            from_=8,
            to=28,
            textvariable=self.height_var,
            width=8,
        ).grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Button(
            control_panel,
            text="生成新迷宫",
            command=self.generate_maze,
            style="Panel.TButton",
        ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(14, 4))

        ttk.Button(
            control_panel,
            text="重新开始闯关",
            command=self.restart_game,
            style="Panel.TButton",
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=4)

        ttk.Button(
            control_panel,
            text="使用 DFS 求解",
            command=lambda: self.run_solver("dfs"),
            style="Panel.TButton",
        ).grid(row=5, column=0, columnspan=2, sticky="ew", pady=4)

        ttk.Button(
            control_panel,
            text="使用 BFS 求解",
            command=lambda: self.run_solver("bfs"),
            style="Panel.TButton",
        ).grid(row=6, column=0, columnspan=2, sticky="ew", pady=4)

        ttk.Button(
            control_panel,
            text="使用 A* 求解",
            command=lambda: self.run_solver("a*"),
            style="Panel.TButton",
        ).grid(row=7, column=0, columnspan=2, sticky="ew", pady=4)

        ttk.Button(
            control_panel,
            text="清除算法提示",
            command=self.clear_solution,
            style="Panel.TButton",
        ).grid(row=8, column=0, columnspan=2, sticky="ew", pady=(4, 14))

        ttk.Label(
            control_panel,
            text="操作说明：方向键 / WASD 移动",
            style="Panel.TLabel",
            wraplength=220,
            justify="left",
        ).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        status_box = ttk.Frame(
            control_panel,
            style="Panel.TFrame",
            width=self.STATUS_BOX_WIDTH,
            height=self.STATUS_BOX_HEIGHT,
        )
        status_box.grid(row=10, column=0, columnspan=2, sticky="ew")
        status_box.grid_propagate(False)

        ttk.Label(
            status_box,
            textvariable=self.status_var,
            style="Panel.TLabel",
            wraplength=self.STATUS_BOX_WIDTH - 10,
            justify="left",
            anchor="nw",
        ).grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(
            container,
            width=self._canvas_width(),
            height=self._canvas_height(),
            bg="#fcfbf7",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=1, sticky="nsew")

    def _canvas_width(self) -> int:
        return self.maze.width * self.CELL_SIZE + self.PADDING * 2

    def _canvas_height(self) -> int:
        return self.maze.height * self.CELL_SIZE + self.PADDING * 2

    def _bind_controls(self) -> None:
        for key in self.MOVE_MAP:
            self.bind(f"<KeyPress-{key}>", self._on_key_press)

    def _reset_player_state(self) -> None:
        self.player_position = self.maze.start
        self.player_path = [self.maze.start]
        self.game_won = False

    def generate_maze(self) -> None:
        self.maze = Maze(self.width_var.get(), self.height_var.get())
        self.current_result = None
        self._reset_player_state()
        self.canvas.config(width=self._canvas_width(), height=self._canvas_height())
        self.status_var.set(
            "已生成新迷宫，采用的是基于迭代 DFS 回溯的生成方法。现在可以自己移动角色闯关，也可以点击按钮查看算法答案。"
        )
        self._draw_maze()

    def restart_game(self) -> None:
        self.current_result = None
        self._reset_player_state()
        self.status_var.set("已回到起点，可以重新挑战当前迷宫。")
        self._draw_maze()

    def clear_solution(self) -> None:
        self.current_result = None
        if self.game_won:
            self.status_var.set("已清除算法提示。你已经成功通关，也可以重新开始再玩一次。")
        else:
            self.status_var.set(
                f"已清除算法提示。你当前手动闯关已经走了 {len(self.player_path) - 1} 步。"
            )
        self._draw_maze()

    def run_solver(self, algorithm: str) -> None:
        self.current_result = solve_maze(self.maze, algorithm)
        self.status_var.set(
            f"你当前手动已走 {len(self.player_path) - 1} 步。"
            f"{self.current_result.algorithm} 共访问 "
            f"{len(self.current_result.explored_order)} 个格子，找到的路径长度为 "
            f"{self.current_result.path_cost}。"
        )
        self._animate_solution(self.current_result)

    def _on_key_press(self, event: tk.Event) -> None:
        move = self.MOVE_MAP.get(event.keysym) or self.MOVE_MAP.get(event.char)
        if move is None:
            return
        direction, (dx, dy) = move
        self._move_player(direction, dx, dy)

    def _move_player(self, direction: str, dx: int, dy: int) -> None:
        if self.game_won:
            self.status_var.set("你已经到达终点了，可以重新开始闯关，或者生成一个新的迷宫。")
            return

        cell = self.maze.cell(self.player_position)
        if cell.walls[direction]:
            self.status_var.set("这个方向有墙，换个方向试试。")
            return

        next_position = (self.player_position[0] + dx, self.player_position[1] + dy)
        self.player_position = next_position
        self.player_path.append(next_position)

        if self.player_position == self.maze.goal:
            self.game_won = True
            self.status_var.set(
                f"恭喜通关。你一共走了 {len(self.player_path) - 1} 步。现在也可以点击 DFS、BFS、A* 按钮，对比算法给出的解法。"
            )
        else:
            self.status_var.set(
                f"你当前位于 {self.player_position[0] + 1} 列，第 {self.player_position[1] + 1} 行；已手动移动 {len(self.player_path) - 1} 步。"
            )

        self._draw_maze()

    def _animate_solution(self, result: SolveResult) -> None:
        self._draw_maze()
        visited = result.explored_order
        index = 0

        def step() -> None:
            nonlocal index
            if index < len(visited):
                self._highlight_cell(visited[index], fill="#cfe8ff")
                index += 1
                self.after(self.VISIT_DELAY_MS, step)
            else:
                self._draw_path(result.path)

        step()

    def _draw_maze(self) -> None:
        self.canvas.delete("all")
        self._draw_cell_background(self.maze.start, "#dff7df")
        self._draw_cell_background(self.maze.goal, "#ffe2d6")

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.grid[y][x]
                x1, y1, x2, y2 = self._cell_bounds((x, y))
                if cell.walls["N"]:
                    self.canvas.create_line(x1, y1, x2, y1, width=2, fill="#3b3b3b")
                if cell.walls["S"]:
                    self.canvas.create_line(x1, y2, x2, y2, width=2, fill="#3b3b3b")
                if cell.walls["W"]:
                    self.canvas.create_line(x1, y1, x1, y2, width=2, fill="#3b3b3b")
                if cell.walls["E"]:
                    self.canvas.create_line(x2, y1, x2, y2, width=2, fill="#3b3b3b")

        self._draw_labels()
        self._draw_player_trail()
        if self.current_result:
            for cell in self.current_result.explored_order:
                self._highlight_cell(cell, fill="#cfe8ff")
            self._draw_path(self.current_result.path)
        self._draw_player()

    def _draw_labels(self) -> None:
        self._draw_center_text(self.maze.start, "起", "#1b5e20")
        self._draw_center_text(self.maze.goal, "终", "#c62828")

    def _draw_player_trail(self) -> None:
        if len(self.player_path) < 2:
            return
        points = []
        for position in self.player_path:
            x1, y1, x2, y2 = self._cell_bounds(position)
            points.extend([(x1 + x2) / 2, (y1 + y2) / 2])
        self.canvas.create_line(*points, fill="#4f83cc", width=3, capstyle=tk.ROUND)

    def _draw_player(self) -> None:
        x1, y1, x2, y2 = self._cell_bounds(self.player_position)
        inset = 7
        self.canvas.create_oval(
            x1 + inset,
            y1 + inset,
            x2 - inset,
            y2 - inset,
            fill="#355c9a",
            outline="#ffffff",
            width=2,
        )

    def _draw_center_text(self, position: tuple[int, int], text: str, color: str) -> None:
        x1, y1, x2, y2 = self._cell_bounds(position)
        self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=text,
            fill=color,
            font=("Helvetica", 12, "bold"),
        )

    def _draw_cell_background(self, position: tuple[int, int], color: str) -> None:
        x1, y1, x2, y2 = self._cell_bounds(position)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def _highlight_cell(self, position: tuple[int, int], fill: str) -> None:
        if position in {self.maze.start, self.maze.goal}:
            return
        x1, y1, x2, y2 = self._cell_bounds(position)
        inset = 6
        self.canvas.create_rectangle(
            x1 + inset,
            y1 + inset,
            x2 - inset,
            y2 - inset,
            fill=fill,
            outline="",
        )

    def _draw_path(self, path: list[tuple[int, int]]) -> None:
        if len(path) < 2:
            self._draw_labels()
            self._draw_player()
            return
        points = []
        for position in path:
            x1, y1, x2, y2 = self._cell_bounds(position)
            points.extend([(x1 + x2) / 2, (y1 + y2) / 2])
        self.canvas.create_line(*points, fill="#f57c00", width=4, capstyle=tk.ROUND)
        self._draw_labels()
        self._draw_player()

    def _cell_bounds(self, position: tuple[int, int]) -> tuple[int, int, int, int]:
        x, y = position
        x1 = self.PADDING + x * self.CELL_SIZE
        y1 = self.PADDING + y * self.CELL_SIZE
        x2 = x1 + self.CELL_SIZE
        y2 = y1 + self.CELL_SIZE
        return x1, y1, x2, y2
