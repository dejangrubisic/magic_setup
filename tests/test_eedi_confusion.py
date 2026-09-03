"""Which wrong misconceptions rank above the true one."""

from collections import Counter

from scripts.eedi_confusion import confused_pairs, distractor_counts

SAMPLES = [
    {"true_id": 1, "top25": [1, 2, 3]},  # rank 1: contributes nothing
    {"true_id": 3, "top25": [2, 5, 3]},  # 2 and 5 above 3
    {"true_id": 5, "top25": [2, 5, 3]},  # 2 above 5
    {"true_id": 9, "top25": [2, 5, 3]},  # absent: everything in the list is above it
]


def test_confused_pairs():
    pairs = confused_pairs(SAMPLES)
    assert pairs == Counter({(3, 2): 1, (3, 5): 1, (5, 2): 1, (9, 2): 1, (9, 5): 1, (9, 3): 1})
    assert confused_pairs(SAMPLES[:1]) == Counter()


def test_distractor_counts():
    assert distractor_counts(SAMPLES) == Counter({2: 3, 5: 2, 3: 1})
