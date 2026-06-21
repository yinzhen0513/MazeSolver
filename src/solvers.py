from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import heapq
from itertools import count

from src.maze import Maze


@dataclass
class SolveResult:
    algorithm: str
    path: list[tuple[int, int]]
    explored_order: list[tuple[int, int]]
    path_cost: int


def _reconstruct_path(
    parent: dict[tuple[int, int], tuple[int, int] | None],
    goal: tuple[int, int],
) -> list[tuple[int, int]]:
    node: tuple[int, int] | None = goal
    path: list[tuple[int, int]] = []
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def depth_first_search(maze: Maze) -> SolveResult:
    stack: list[tuple[tuple[int, int], tuple[int, int] | None]] = [(maze.start, None)]
    visited: set[tuple[int, int]] = set()
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    explored_order: list[tuple[int, int]] = []

    while stack:
        node, prev = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        parent[node] = prev
        explored_order.append(node)
        if node == maze.goal:
            path = _reconstruct_path(parent, maze.goal)
            return SolveResult("DFS", path, explored_order, maze.path_cost(path))

        for neighbor in reversed(maze.accessible_neighbors(node)):
            if neighbor not in visited:
                stack.append((neighbor, node))

    return SolveResult("DFS", [], explored_order, 0)


def breadth_first_search(maze: Maze) -> SolveResult:
    queue = deque([maze.start])
    visited = {maze.start}
    parent: dict[tuple[int, int], tuple[int, int] | None] = {maze.start: None}
    explored_order: list[tuple[int, int]] = []

    while queue:
        node = queue.popleft()
        explored_order.append(node)
        if node == maze.goal:
            path = _reconstruct_path(parent, maze.goal)
            return SolveResult("BFS", path, explored_order, maze.path_cost(path))

        for neighbor in maze.accessible_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                queue.append(neighbor)

    return SolveResult("BFS", [], explored_order, 0)


def a_star_search(maze: Maze) -> SolveResult:
    def heuristic(node: tuple[int, int]) -> int:
        return abs(node[0] - maze.goal[0]) + abs(node[1] - maze.goal[1])

    tie_breaker = count()
    start_h = heuristic(maze.start)
    frontier: list[tuple[int, int, int, int, tuple[int, int]]] = [
        (start_h, start_h, next(tie_breaker), 0, maze.start)
    ]
    parent: dict[tuple[int, int], tuple[int, int] | None] = {maze.start: None}
    cost: dict[tuple[int, int], int] = {maze.start: 0}
    explored_order: list[tuple[int, int]] = []
    visited: set[tuple[int, int]] = set()

    while frontier:
        _, _, _, current_cost, node = heapq.heappop(frontier)
        if node in visited:
            continue
        visited.add(node)
        explored_order.append(node)

        if node == maze.goal:
            path = _reconstruct_path(parent, maze.goal)
            return SolveResult("A*", path, explored_order, current_cost)

        for neighbor in sorted(maze.accessible_neighbors(node), key=heuristic):
            next_cost = current_cost + 1
            if next_cost < cost.get(neighbor, float("inf")):
                cost[neighbor] = next_cost
                parent[neighbor] = node
                next_h = heuristic(neighbor)
                priority = next_cost + next_h
                heapq.heappush(
                    frontier,
                    (priority, next_h, next(tie_breaker), next_cost, neighbor),
                )

    return SolveResult("A*", [], explored_order, 0)


def solve_maze(maze: Maze, algorithm: str) -> SolveResult:
    normalized = algorithm.strip().lower()
    if normalized == "dfs":
        return depth_first_search(maze)
    if normalized == "bfs":
        return breadth_first_search(maze)
    if normalized in {"a*", "astar", "a-star"}:
        return a_star_search(maze)
    raise ValueError(f"Unsupported algorithm: {algorithm}")
