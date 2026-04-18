"""
Tests for interactive UI helpers.
"""

from src.scraper import Giveaway
from src.ui import SimpleTUI


def test_build_choices_includes_all_giveaways():
    giveaways = [
        Giveaway("First", "https://gleam.io/giveaways/AAA11", "First description"),
        Giveaway("Second", "https://gleam.io/giveaways/BBB22", "Second description"),
        Giveaway("Third", "https://gleam.io/giveaways/CCC33", "Third description"),
    ]
    ui = SimpleTUI(giveaways)
    choices = ui._build_choices()

    assert len(choices) == 3
    assert choices[0][0] == "0"
    assert "First" in choices[0][1]
    assert choices[2][0] == "2"
    assert "Third" in choices[2][1]


def test_build_choices_truncates_long_description():
    long_description = "x" * 120
    giveaways = [Giveaway("Long", "https://gleam.io/giveaways/DDD44", long_description)]
    ui = SimpleTUI(giveaways)
    label = ui._build_choices()[0][1]

    assert "..." in label
