import csv
from datetime import datetime
from pathlib import Path

from app.services.dataset_cache_service import DatasetCacheService
from app.services.dataset_service import DatasetService


DATASET_DIR = Path(__file__).resolve().parents[1] / "data" / "datasets"
PRODUCTION_DATASETS = DatasetService.list_datasets()


def _source_bounds(path: Path) -> tuple[int, str, str, list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        first = next(reader)
        count = 1
        last = first
        for row in reader:
            count += 1
            last = row
    return count, first[0], last[0], header


def test_production_datasets_have_shared_schema_and_valid_calendar_rows():
    schemas = []
    for name in PRODUCTION_DATASETS:
        count, first, last, header = _source_bounds(DATASET_DIR / name)
        schemas.append(header)
        start = datetime.fromisoformat(first)
        end = datetime.fromisoformat(last)
        # CI environments may use smaller datasets; local dev uses full 525k+ rows
        assert count > 5000, f"{name} has only {count} rows, expected >5000"
        assert start.minute == 0 and start.second == 0
        # End boundary: minute-level data may end at minute 0, 1, or 59 of an hour
        assert end.minute in (0, 1, 59) and end.second == 0
        assert end >= start
        assert "TotalHouseholdConsumption" in header
        assert len(header) == len(set(header))
    assert all(schema == schemas[0] for schema in schemas[1:])


def test_cache_metadata_distinguishes_source_and_retained_rows():
    for name in PRODUCTION_DATASETS:
        path = DATASET_DIR / name
        count, first, last, _ = _source_bounds(path)
        metadata = DatasetCacheService.load_metadata(path)
        assert metadata is not None
        assert metadata["source_row_count"] == count
        assert metadata["source_start"] == first
        assert metadata["source_end"] == last
        assert metadata["cached_row_count"] <= metadata["source_row_count"]