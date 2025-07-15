import csv
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def load_year_data(data_dir: Path, year: int) -> Dict[str, Any]:
    """
    Loads all workout data from CSV files in data/{year}/ subdirectories.
    Returns a dictionary structured as:
    {
        year: [
            {
                month: [
                    {"metadata": pd.DataFrame, "data": pd.DataFrame}
                ]
            }
        ]
    }
    """
    year_path = Path(data_dir) / str(year)
    months = sorted(
        [p for p in year_path.iterdir() if p.is_dir()], key=lambda x: int(x.name)
    )
    result = {str(year): {}}
    for month_path in months:
        month_list = []
        for csv_file in month_path.glob("*.CSV"):
            with csv_file.open("r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                if len(rows) > 2:
                    metadata_header = rows[0]
                    metadata_values = rows[1]
                    metadata_dict = dict(zip(metadata_header, metadata_values))
                    data_header = rows[2]
                    data_rows = [
                        row for row in rows[3:] if any(cell.strip() for cell in row)
                    ]
                    data_df = pd.DataFrame(data_rows, columns=data_header)
                    month_list.append({"metadata": metadata_dict, "data": data_df})
        result[str(year)][month_path.name] = month_list
    return result


def load_all_years_data(data_dir: Path) -> Dict[str, Any]:
    """
    Loads all workout data from all years in the data directory.
    Returns a dictionary structured as:
    {
        year: {
            month: [
                {"metadata": dict, "data": pd.DataFrame}
            ]
        }
    }
    """
    all_data = {}
    for year_path in sorted(
        [p for p in Path(data_dir).iterdir() if p.is_dir()], key=lambda x: int(x.name)
    ):
        year = int(year_path.name)
        all_data.update(load_year_data(data_dir, year))
    return all_data
