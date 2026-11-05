import pytest

from brief import soe_note
from ingest.paths import MARTS

pytestmark = pytest.mark.skipif(
    not (MARTS / "mart_education_completions.parquet").exists(),
    reason="run make soe-note first",
)


@pytest.fixture(scope="module")
def numbers():
    return soe_note.numbers(soe_note.con())


def test_series_changes_add_to_the_total(numbers):
    assert sum(numbers["ba_series"].values()) == numbers["ba_total_change"]


def test_groups_add_to_the_mapped_total(numbers):
    assert sum(numbers["groups"].values()) == numbers["mapped_total"]
    assert 0 < numbers["medium"] < numbers["mapped_total"]


def test_rank_and_counts_in_range(numbers):
    assert 1 <= numbers["ma_rank"] <= 18
    assert 0 <= numbers["ma_peers_grew"] <= 17
    assert 0 < numbers["high_share"] < 1


def test_note_matches_the_pinned_anchors(numbers):
    # The same 2014-15 and 2024-25 values transform/tests/assert_education_anchors.sql pins,
    # seen through the three-year windows the note reports.
    assert round(numbers["ba"]["early"]) == 122 and round(numbers["ba"]["late"]) == 180
    assert numbers["ma_latest"] == 164
