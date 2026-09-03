import matplotlib
import numpy as np
import pandas as pd

from magic.plots import bar_with_ci, heatmap


def test_matplotlib_backend_is_headless():
    assert matplotlib.get_backend().lower() == "agg"


def test_bar_with_ci_saves_a_png(tmp_path):
    out = tmp_path / "figs" / "bars.png"
    fig = bar_with_ci(
        ["base", "tuned"], [0.50, 0.62], [0.44, 0.55], [0.56, 0.69], title="accuracy", path=out
    )
    assert out.stat().st_size > 1000
    ax = fig.axes[0]
    assert ax.get_title() == "accuracy"
    assert [t.get_text() for t in ax.get_xticklabels()] == ["base", "tuned"]
    assert [p.get_height() for p in ax.patches] == [0.50, 0.62]


def test_bar_with_ci_without_a_path_writes_nothing(tmp_path):
    bar_with_ci(["a"], [1.0], [0.5], [1.5])
    assert list(tmp_path.iterdir()) == []


def test_heatmap_annotates_every_cell(tmp_path):
    df = pd.DataFrame(
        [[0.5, 1.0], [1.0, np.nan]], index=["math", "code"], columns=["run-a", "run-b"]
    )
    out = tmp_path / "heat.png"
    fig = heatmap(df, title="by category", path=out)
    assert out.stat().st_size > 1000
    texts = [t.get_text() for t in fig.axes[0].texts]
    assert texts == ["0.50", "1.00", "1.00", "nan"]
    assert [t.get_text() for t in fig.axes[0].get_yticklabels()] == ["math", "code"]


def test_line_with_ci_saves_a_png(tmp_path):
    from magic.plots import line_with_ci

    x = [0, 1, 2]
    fig = line_with_ci(
        {"a": (x, [0.1, 0.5, 0.9], [0.0, 0.4, 0.8], [0.2, 0.6, 1.0])},
        title="t",
        path=tmp_path / "c.png",
    )
    assert fig is not None
    assert (tmp_path / "c.png").stat().st_size > 0
