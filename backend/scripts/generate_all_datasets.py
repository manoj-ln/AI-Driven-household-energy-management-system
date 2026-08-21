"""Generate all enterprise synthetic household energy datasets.

Outputs (into backend/data/datasets/):
  - Dataset_Working_Household.csv    (2023-2025, per-minute, ~100+ devices)
  - Dataset_Business_Household.csv   (2024-2025, per-minute, ~100+ devices)
  - Dataset_Smart_Eco_Household.csv  (2024-2025, per-minute, ~100+ devices, solar+EV)
  - energy_dataset_2024.csv          (compact 2021-style schema, full year)
  - energy_dataset_2025.csv          (compact 2021-style schema, full year)
  - energy_dataset_merged_3years.csv (2021 + 2024 + 2025, compact schema)

All datasets share the identical wide schema (metadata columns + device
columns) and are fully deterministic given the fixed seeds.
"""

from __future__ import annotations

import csv
import multiprocessing as mp
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATASETS_DIR = BASE_DIR / "data" / "datasets"

# Compact 2021-style column layout preserved by the slim writer.
SLIM_COLUMNS: dict[str, str] = {
    "Fridge_Main": "Refrigerator_Main",
    "TV_Living": "Television_Living",
    "Ceiling_Fan_Living": "Ceiling_Fan_Living",
    "Ceiling_Fan_Master": "Ceiling_Fan_Bed1",
    "Phone_Charger_1": "Phone_Charger_1",
    "Exhaust_Fan": "Exhaust_Fan_Bath",
    "Iron_Box": "Iron_Box",
    "Geyser_1": "Geyser_Bathroom1",
}

WS = "working"
BS = "business"


def build_base_scenario(year: int):
    """Scenario used to regenerate compact 2021-style reference years."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from dataset_simulator.config import BASE_YEAR_FLAGS, Scenario
    return Scenario(
        name="base",
        label=f"energy_dataset_{year}",
        years=[year],
        power_flags=BASE_YEAR_FLAGS,
        electricity_tariff="residential_slabbed",
        uses_renewables=False,
        base_cost_pu=6.26,
        note="Compact reference household (matches 2021 schema).",
    )


def _generate_full(kwargs: dict) -> dict:
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from dataset_simulator.config import SCENARIOS
    from dataset_simulator.simulator import Simulator

    datasets_dir = Path(kwargs["datasets_dir"])
    scenario = SCENARIOS[kwargs["name"]]
    print(f"[{scenario.name}] generating {scenario.label} "
          f"({scenario.years[0]}-{scenario.years[-1]})...", flush=True)
    sim = Simulator(scenario, seed=kwargs["seed"])
    stats = sim.run(datasets_dir / f"{scenario.label}.csv")
    print(f"[{scenario.name}] done: {stats}", flush=True)
    return stats


def _generate_slim(kwargs: dict) -> dict:
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from dataset_simulator.simulator import Simulator

    datasets_dir = Path(kwargs["datasets_dir"])
    scenario = kwargs["scenario"]
    print(f"[slim:{scenario.years[0]}] generating {scenario.label}...", flush=True)
    sim = Simulator(
        scenario,
        seed=kwargs["seed"],
        cold_bias=kwargs.get("cold_bias", 0.0),
        hot_bias=kwargs.get("hot_bias", 0.0),
        slim_columns=SLIM_COLUMNS,
    )
    stats = sim.run(datasets_dir / f"{scenario.label}.csv")
    print(f"[slim:{scenario.years[0]}] done: {stats}", flush=True)
    return stats


def _merge_reference_years() -> None:
    """Concatenate 2021 (existing) + 2024 + 2025 into merged_3years file."""
    datasets_dir = DATASETS_DIR
    year_files = ["energy_dataset_2021.csv", "energy_dataset_2024.csv", "energy_dataset_2025.csv"]
    output = datasets_dir / "energy_dataset_merged_3years.csv"

    if not (datasets_dir / "energy_dataset_2021.csv").exists():
        raise FileNotFoundError("energy_dataset_2021.csv missing - cannot build merged file.")

    header = None
    row_count = 0
    first_ts = None
    last_ts = None
    with output.open("w", newline="", encoding="utf-8") as out_fh:
        writer = csv.writer(out_fh)
        for filename in year_files:
            path = datasets_dir / filename
            with path.open("r", newline="", encoding="utf-8") as in_fh:
                reader = csv.reader(in_fh)
                file_header = next(reader)
                if header is None:
                    header = file_header
                    writer.writerow(header)
                elif file_header != header:
                    raise ValueError(f"Schema mismatch in {filename}")
                for row in reader:
                    if not row:
                        continue
                    if len(row) != len(header):
                        raise ValueError(f"Column count mismatch in {filename}")
                    writer.writerow(row)
                    row_count += 1
                    if first_ts is None:
                        first_ts = row[0]
                    last_ts = row[0]

    print(f"[merged] {output.name}: {row_count:,} rows "
          f"({first_ts} -> {last_ts})", flush=True)


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    tasks = [
        {"name": WS, "seed": 11, "datasets_dir": str(DATASETS_DIR)},
        {"name": BS, "seed": 21, "datasets_dir": str(DATASETS_DIR)},
        {"name": "eco", "seed": 31, "datasets_dir": str(DATASETS_DIR)},
        {"scenario": build_base_scenario(2024), "seed": 41, "hot_bias": 0.3, "datasets_dir": str(DATASETS_DIR)},
        {"scenario": build_base_scenario(2025), "seed": 51, "hot_bias": 0.6, "datasets_dir": str(DATASETS_DIR)},
    ]

    nproc = min(5, mp.cpu_count() or 1)
    print(f"Using {nproc} worker processes.", flush=True)

    with mp.Pool(nproc) as pool:
        futures = []
        for task in tasks:
            if "name" in task:
                futures.append(pool.apply_async(_generate_full, (task,)))
            else:
                futures.append(pool.apply_async(_generate_slim, (task,)))
        for future in futures:
            future.get()

    _merge_reference_years()
    print("All datasets generated successfully.", flush=True)


if __name__ == "__main__":
    main()
