import argparse
import logging
from pathlib import Path

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from polar.flow_client import PolarFlowClient
from polar.organize_downloads import organize_files_by_date


def main():
    parser = argparse.ArgumentParser(description="Polar Flow Data Downloader CLI")
    parser.add_argument("output_dir", help="Directory to save downloaded files")
    parser.add_argument(
        "--organizer", action="store_true", help="File organizer to use after download"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Run the Selenium download logic. If not set, only organization will run.",
    )
    parser.add_argument("--username", help="Polar Flow username", required=False)
    parser.add_argument("--password", help="Polar Flow password", required=False)
    parser.add_argument("--year", help="Year to download exercises for", required=False)

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if args.download:
        # Check required arguments for download
        if not (args.username and args.password and args.year):
            parser.error("--download requires --username, --password, and --year.")

        home = Path(__file__).parent
        chrome_bin = home / "chrome-linux64" / "chrome"
        chromedriver_path = home / "chromedriver"

        options = Options()
        options.binary_location = str(chrome_bin)

        service = Service(str(chromedriver_path))
        driver = Chrome(service=service, options=options)
        client = PolarFlowClient(driver)

        try:
            logging.info("Starting login process...")
            client.login(args.username, args.password)
            exercise_ids = client.get_all_exercise_ids_for_year(args.year)
            logging.info(f"Preparing to export {len(exercise_ids)} exercises.")
            for ex_id in exercise_ids:
                logging.info(f"Exporting exercise ID: {ex_id}")
                client.export_exercise(ex_id, args.output_dir)
        finally:
            driver.quit()

    # Organizer logic
    if args.organizer:
        logging.info(f"Organizing files in {args.output_dir}")
        organize_files_by_date(args.output_dir)
        logging.info("Organization complete.")


if __name__ == "__main__":
    main()
