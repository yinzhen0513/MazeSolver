import unittest

from src.maze import Maze


class MazeTests(unittest.TestCase):
    def test_every_cell_is_reachable(self) -> None:
        maze = Maze(10, 10, seed=7)
        stack = [maze.start]
        visited = {maze.start}

        while stack:
            node = stack.pop()
            for neighbor in maze.accessible_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)

        self.assertEqual(len(visited), maze.width * maze.height)

    def test_ascii_export_marks_start_and_goal(self) -> None:
        maze = Maze(4, 4, seed=11)
        ascii_map = maze.to_ascii()
        self.assertIn(" S ", ascii_map)
        self.assertIn(" G ", ascii_map)

    def test_default_maze_has_extra_loops(self) -> None:
        maze = Maze(8, 8, seed=5)
        edge_count = 0
        for y in range(maze.height):
            for x in range(maze.width):
                edge_count += len(maze.accessible_neighbors((x, y)))
        edge_count //= 2
        self.assertGreater(edge_count, maze.width * maze.height - 1)


if __name__ == "__main__":
    unittest.main()
