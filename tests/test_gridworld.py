import numpy as np
from tasks.gridworld import (
    GOAL_REWARD,
    STEP_PENALTY,
    GridEnv,
    Level,
    QAgent,
    bfs_shortest_path,
    make_heldout,
    make_level,
    make_pool,
)


def _open_level(size: int = 5) -> Level:
    grid = np.zeros((size, size), dtype=bool)
    return Level("open", grid, (0, 0), (size - 1, size - 1), 0.0, 2 * (size - 1))


def test_step_into_wall_or_off_grid_stays_put():
    grid = np.zeros((3, 3), dtype=bool)
    grid[0, 1] = True
    env = GridEnv(Level("w", grid, (0, 0), (2, 2), 0.0, 4))
    env.reset()
    env.step(0)  # up, off grid
    assert env.pos == (0, 0)
    env.step(3)  # right, into wall
    assert env.pos == (0, 0)
    env.step(1)  # down, free
    assert env.pos == (1, 0)


def test_step_penalty_goal_reward_and_done():
    env = GridEnv(_open_level(3))
    env.reset()
    _, r, done = env.step(1)
    assert r == STEP_PENALTY
    assert not done
    env.step(1)
    env.step(3)
    _, r, done = env.step(3)
    assert r == GOAL_REWARD
    assert done
    assert env.pos == (2, 2)


def test_episode_ends_after_max_steps():
    env = GridEnv(_open_level(5), max_steps=7)
    env.reset()
    dones = [env.step(0)[2] for _ in range(7)]  # bump into the top wall forever
    assert dones == [False] * 6 + [True]
    assert env.pos == (0, 0)


def test_make_level_is_deterministic_and_ids_differ():
    a = make_level(3, 7, 0.25, 4)
    b = make_level(3, 7, 0.25, 4)
    assert np.array_equal(a.grid, b.grid)
    assert (a.start, a.goal) == (b.start, b.goal)
    grids = [make_level(i, 7, 0.25, 4).grid for i in range(5)]
    assert any(not np.array_equal(grids[0], g) for g in grids[1:])


def test_generated_levels_are_solvable_and_far_enough():
    for lvl in make_pool(40, seed=3):
        assert bfs_shortest_path(lvl.grid, lvl.start, lvl.goal) == lvl.path_len
        assert lvl.path_len is not None
        assert not lvl.grid[lvl.start]
        assert not lvl.grid[lvl.goal]
    lvl = make_level(11, 9, 0.3, 8)
    assert abs(lvl.start[0] - lvl.goal[0]) + abs(lvl.start[1] - lvl.goal[1]) >= 8


def test_heldout_is_hard_and_fixed():
    held = make_heldout(5, min_path_len=12)
    assert len(held) == 5
    assert all(lvl.size == 9 and lvl.path_len >= 12 for lvl in held)
    assert [lvl.id for lvl in held] == [lvl.id for lvl in make_heldout(5, min_path_len=12)]


def test_bfs_unsolvable_and_open_grid():
    grid = np.zeros((4, 4), dtype=bool)
    assert bfs_shortest_path(grid, (0, 0), (3, 3)) == 6
    grid[1, :] = True  # full wall row
    assert bfs_shortest_path(grid, (0, 0), (3, 3)) is None


def test_q_agent_learns_tiny_open_level():
    lvl = _open_level(5)
    agent = QAgent(seed=0, eps_decay_steps=2000)
    assert not agent.solves(lvl)  # untrained greedy agent bumps around, does not reach the goal
    for _ in range(300):
        agent.run_episode(lvl)
    assert agent.solves(lvl)
