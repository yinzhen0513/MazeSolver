import unittest

from src.maze import Maze
from src.solvers import a_star_search, breadth_first_search, depth_first_search


class SolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.maze = Maze(12, 12, seed=21)

    def test_bfs_and_a_star_find_shortest_paths(self) -> None:
        bfs = breadth_first_search(self.maze)
        a_star = a_star_search(self.maze)
        self.assertTrue(bfs.path)
        self.assertEqual(bfs.path[0], self.maze.start)
        self.assertEqual(bfs.path[-1], self.maze.goal)
        self.assertEqual(bfs.path_cost, a_star.path_cost)

    def test_dfs_finds_a_valid_path(self) -> None:
        dfs = depth_first_search(self.maze)
        self.assertTrue(dfs.path)
        self.assertEqual(dfs.path[0], self.maze.start)
        self.assertEqual(dfs.path[-1], self.maze.goal)

    def test_bfs_is_not_worse_than_dfs(self) -> None:
        bfs = breadth_first_search(self.maze)
        dfs = depth_first_search(self.maze)
        self.assertLessEqual(bfs.path_cost, dfs.path_cost)

    def test_seeded_maze_can_produce_different_algorithm_paths(self) -> None:
        dfs = depth_first_search(self.maze)
        bfs = breadth_first_search(self.maze)
        self.assertNotEqual(dfs.path, bfs.path)


if __name__ == "__main__":
    unittest.main()
