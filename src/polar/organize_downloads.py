from datetime import datetime
from pathlib import Path


def organize_files_by_date(download_dir: str | Path):
    """
    Organizes files in the download_dir into year/month subfolders based on the file's date in the filename.
    Assumes filenames contain a date in the format YYYY-MM-DD (e.g., ..._2022-09-27_06-35-25.CSV).
    """
    download_path = Path(download_dir)
    # Recursively find all CSV files (case-insensitive)
    for file_path in download_path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() != ".csv":
            continue
        filename = file_path.name
        parts = filename.split("_")
        if len(parts) < 2:
            continue
        date_str = parts[-2]  # e.g., '2022-09-27'
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        year = str(date_obj.year)
        month = f"{date_obj.month:02d}"
        target_dir = download_path / year / month
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename
        # Only move if not already in the correct place
        if file_path.resolve() != target_path.resolve():
            file_path.replace(target_path)


if __name__ == "__main__":
    # Example usage
    organize_files_by_date("data")
