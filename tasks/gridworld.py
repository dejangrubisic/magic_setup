"""Procedural gridworld, seeded level generator, BFS difficulty proxy, tabular Q-learning agent."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

# Actions: up, down, left, right (row, col deltas).
MOVES = np.array([(-1, 0), (1, 0), (0, -1), (0, 1)])
N_ACTIONS = 4
STEP_PENALTY = -0.01
GOAL_REWARD = 1.0
MAX_STEPS = 100
SIZES = (5, 7, 9)


@dataclass(frozen=True)
class Level:
    """One level; `grid[r, c]` is True for a wall. `path_len` is the BFS shortest path."""

    id: str
    grid: np.ndarray
    start: tuple[int, int]
    goal: tuple[int, int]
    wall_density: float
    path_len: int

    @property
    def size(self) -> int:
        return int(self.grid.shape[0])


def bfs_shortest_path(
    grid: np.ndarray, start: tuple[int, int], goal: tuple[int, int]
) -> int | None:
    """Number of moves on the shortest start->goal path through free cells, or None if unreachable."""
    n = grid.shape[0]
    dist = -np.ones((n, n), dtype=np.int64)
    dist[start] = 0
    q: deque[tuple[int, int]] = deque([start])
    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            return int(dist[r, c])
        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not grid[nr, nc] and dist[nr, nc] < 0:
                dist[nr, nc] = dist[r, c] + 1
                q.append((nr, nc))
    return None


def make_level(level_id: int, size: int, wall_density: float, min_dist: int) -> Level:
    """Deterministic solvable level: the grid depends only on the four arguments.

    Walls are Bernoulli(wall_density); start/goal are free cells at manhattan distance >= min_dist.
    Draws are retried (with a fresh sub-seed) until BFS finds a path.
    """
    min_dist = min(min_dist, 2 * (size - 1))
    for attempt in range(1000):
        rng = np.random.default_rng([level_id, size, round(wall_density * 1000), min_dist, attempt])
        grid = rng.random((size, size)) < wall_density
        free = np.argwhere(~grid)
        if len(free) < 2:
            continue
        s = tuple(int(x) for x in free[rng.integers(len(free))])
        far = free[np.abs(free - s).sum(axis=1) >= min_dist]
        if len(far) == 0:
            continue
        g = tuple(int(x) for x in far[rng.integers(len(far))])
        path_len = bfs_shortest_path(grid, s, g)
        if path_len is not None:
            return Level(
                f"L{level_id}-s{size}-w{wall_density:.2f}-d{min_dist}",
                grid,
                s,
                g,
                wall_density,
                path_len,
            )
    raise RuntimeError(
        f"no solvable level after 1000 attempts: {level_id=} {size=} {wall_density=}"
    )


def make_pool(n: int = 500, seed: int = 0, id_offset: int = 0) -> list[Level]:
    """Training pool: sizes uniform over SIZES, wall density U(0.1, 0.35), min_dist U{2..size}."""
    rng = np.random.default_rng(seed)
    pool = []
    for i in range(n):
        size = int(rng.choice(SIZES))
        density = float(np.round(rng.uniform(0.1, 0.35), 2))
        min_dist = int(rng.integers(2, size + 1))
        pool.append(make_level(id_offset + i, size, density, min_dist))
    return pool


def make_heldout(
    n: int = 30, min_path_len: int = 10, density: tuple[float, float] = (0.10, 0.20), seed: int = 1
) -> list[Level]:
    """Fixed hard eval set: size 9, shortest path >= min_path_len (pool mean is ~9 for size 9).

    Wall density defaults to the low end of the pool: at 0.25-0.35 with path >= 12 the tabular
    agent scores 0 for every curriculum (no signal), so 'hard' here means long path, not dense.
    """
    rng = np.random.default_rng(seed)
    out: list[Level] = []
    level_id = 100_000
    while len(out) < n:
        wall = float(np.round(rng.uniform(*density), 2))
        lvl = make_level(level_id, 9, wall, 8)
        level_id += 1
        if lvl.path_len >= min_path_len:
            out.append(lvl)
    return out


class GridEnv:
    """Deterministic 4-action gridworld over one Level; observations are local + goal-relative."""

    def __init__(self, level: Level, max_steps: int = MAX_STEPS) -> None:
        self.level = level
        self.max_steps = max_steps
        self.pos = level.start
        self.t = 0

    def reset(self) -> tuple:
        self.pos, self.t = self.level.start, 0
        return self.obs()

    def obs(self) -> tuple:
        """Clipped goal offset plus the 3x3 wall neighbourhood: shared across levels."""
        r, c = self.pos
        n = self.level.size
        dr = int(np.clip(self.level.goal[0] - r, -4, 4))
        dc = int(np.clip(self.level.goal[1] - c, -4, 4))
        walls = []
        for ddr in (-1, 0, 1):
            for ddc in (-1, 0, 1):
                if ddr == 0 and ddc == 0:
                    continue
                rr, cc = r + ddr, c + ddc
                walls.append(not (0 <= rr < n and 0 <= cc < n) or bool(self.level.grid[rr, cc]))
        return (dr, dc, *walls)

    def step(self, action: int) -> tuple[tuple, float, bool]:
        """Move if the target cell is free and in bounds; else stay. Returns (obs, reward, done)."""
        n = self.level.size
        r, c = self.pos
        nr, nc = r + int(MOVES[action][0]), c + int(MOVES[action][1])
        if 0 <= nr < n and 0 <= nc < n and not self.level.grid[nr, nc]:
            self.pos = (nr, nc)
        self.t += 1
        if self.pos == self.level.goal:
            return self.obs(), GOAL_REWARD, True
        return self.obs(), STEP_PENALTY, self.t >= self.max_steps


class QAgent:
    """Tabular Q-learning on the shared observation; epsilon-greedy with linear epsilon decay."""

    def __init__(
        self,
        seed: int = 0,
        alpha: float = 0.2,
        gamma: float = 0.95,
        eps_start: float = 1.0,
        eps_end: float = 0.05,
        eps_decay_steps: int = 100_000,
    ) -> None:
        self.rng = np.random.default_rng(seed)
        self.alpha, self.gamma = alpha, gamma
        self.eps_start, self.eps_end, self.eps_decay_steps = eps_start, eps_end, eps_decay_steps
        self.q: dict[tuple, np.ndarray] = {}
        self.steps = 0

    def values(self, obs: tuple) -> np.ndarray:
        v = self.q.get(obs)
        if v is None:
            v = self.q[obs] = np.zeros(N_ACTIONS)
        return v

    @property
    def epsilon(self) -> float:
        frac = min(1.0, self.steps / max(1, self.eps_decay_steps))
        return self.eps_start + frac * (self.eps_end - self.eps_start)

    def act(self, obs: tuple, greedy: bool = False) -> int:
        if not greedy and self.rng.random() < self.epsilon:
            return int(self.rng.integers(N_ACTIONS))
        v = self.values(obs)
        best = np.flatnonzero(v == v.max())
        return int(best[0]) if greedy else int(self.rng.choice(best))

    def update(self, obs: tuple, action: int, reward: float, next_obs: tuple, done: bool) -> float:
        """One Q-learning backup; returns the absolute TD error."""
        target = reward if done else reward + self.gamma * self.values(next_obs).max()
        td = target - self.values(obs)[action]
        self.q[obs][action] += self.alpha * td
        self.steps += 1
        return abs(float(td))

    def run_episode(self, level: Level) -> tuple[bool, float, int]:
        """Train for one episode on `level`; returns (solved, mean |TD error|, steps used)."""
        env = GridEnv(level)
        obs = env.reset()
        td_sum, done, reward = 0.0, False, 0.0
        while not done:
            a = self.act(obs)
            next_obs, reward, done = env.step(a)
            td_sum += self.update(obs, a, reward, next_obs, done)
            obs = next_obs
        return reward == GOAL_REWARD, td_sum / env.t, env.t

    def solves(self, level: Level) -> bool:
        """Greedy rollout; True if the goal is reached within max_steps."""
        env = GridEnv(level)
        obs = env.reset()
        done, reward = False, 0.0
        while not done:
            obs, reward, done = env.step(self.act(obs, greedy=True))
        return reward == GOAL_REWARD


class RandomCurriculum:
    """Uniform sampling from the pool; ignores feedback."""

    def __init__(self, pool: list[Level], seed: int = 0) -> None:
        self.pool = pool
        self.rng = np.random.default_rng(seed)

    def sample(self) -> Level:
        return self.pool[int(self.rng.integers(len(self.pool)))]

    def update(self, level: Level, solved: bool, td_error: float, steps_used: int) -> None:
        pass


class Easy2Hard:
    """Sliding window over the pool sorted by shortest-path length, advanced by env steps used."""

    def __init__(self, pool: list[Level], total_steps: int, seed: int = 0, window: float = 0.25):
        self.sorted = sorted(pool, key=lambda lvl: lvl.path_len)
        self.total_steps = total_steps
        self.window = window
        self.rng = np.random.default_rng(seed)
        self.steps = 0

    def sample(self) -> Level:
        n = len(self.sorted)
        frac = min(1.0, self.steps / max(1, self.total_steps))
        hi = max(1, round(frac * n))
        lo = max(0, round((frac - self.window) * n))
        hi = max(hi, lo + 1)
        return self.sorted[int(self.rng.integers(lo, hi))]

    def update(self, level: Level, solved: bool, td_error: float, steps_used: int) -> None:
        self.steps += steps_used


class PLRLite:
    """Prioritised level replay, lite: a bounded buffer ranked by score, rank-based sampling.

    With probability `p_replay` a buffered level is drawn with probability proportional to
    1/rank (rank 1 = highest score); otherwise a uniform pool level is drawn. After each episode
    the level's score is an EMA of |TD error| (`score="td"`) or of 1 - solved (`score="unsolved"`),
    and the lowest-scored level is evicted when the buffer exceeds `buffer_size`.
    """

    def __init__(
        self,
        pool: list[Level],
        seed: int = 0,
        buffer_size: int = 100,
        p_replay: float = 0.5,
        score: str = "td",
        ema: float = 0.5,
    ) -> None:
        if score not in ("td", "unsolved"):
            raise ValueError(f"score must be 'td' or 'unsolved', got {score!r}")
        self.pool = pool
        self.rng = np.random.default_rng(seed)
        self.buffer_size, self.p_replay, self.score_kind, self.ema = (
            buffer_size,
            p_replay,
            score,
            ema,
        )
        self.buffer: dict[str, tuple[Level, float]] = {}

    def sample(self) -> Level:
        if self.buffer and self.rng.random() < self.p_replay:
            ranked = sorted(self.buffer.values(), key=lambda t: -t[1])
            w = 1.0 / np.arange(1, len(ranked) + 1)
            return ranked[int(self.rng.choice(len(ranked), p=w / w.sum()))][0]
        return self.pool[int(self.rng.integers(len(self.pool)))]

    def update(self, level: Level, solved: bool, td_error: float, steps_used: int) -> None:
        new = td_error if self.score_kind == "td" else 1.0 - float(solved)
        old = self.buffer[level.id][1] if level.id in self.buffer else new
        self.buffer[level.id] = (level, self.ema * new + (1 - self.ema) * old)
        if len(self.buffer) > self.buffer_size:
            worst = min(self.buffer, key=lambda k: self.buffer[k][1])
            del self.buffer[worst]


def evaluate(agent: QAgent, levels: list[Level]) -> list[int]:
    """1 if the greedy policy solves each level, else 0."""
    return [int(agent.solves(lvl)) for lvl in levels]


def train(
    curriculum,
    heldout: list[Level],
    agent: QAgent,
    steps_per_ckpt: int,
    n_ckpts: int,
) -> list[dict]:
    """Train until n_ckpts * steps_per_ckpt env steps; evaluate on heldout at step 0 and each ckpt."""
    rows = [{"id": "ckpt0", "steps": 0, "solve_rate": 0.0, "per_level": evaluate(agent, heldout)}]
    rows[0]["solve_rate"] = float(np.mean(rows[0]["per_level"]))
    steps, next_ckpt, k = 0, steps_per_ckpt, 1
    while k <= n_ckpts:
        level = curriculum.sample()
        solved, td, used = agent.run_episode(level)
        curriculum.update(level, solved, td, used)
        steps += used
        if steps >= next_ckpt:
            per = evaluate(agent, heldout)
            rows.append(
                {
                    "id": f"ckpt{k}",
                    "steps": steps,
                    "solve_rate": float(np.mean(per)),
                    "per_level": per,
                }
            )
            next_ckpt += steps_per_ckpt
            k += 1
    return rows
