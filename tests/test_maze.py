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


if __name__ == "__main__":
    unittest.main()
