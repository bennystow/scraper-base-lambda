import json
import sys
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from src.utils.utils import (
    get_chrome_options,
    get_chrome_service,
    is_running_in_docker,
)

logger = logging.getLogger(__name__)


class ScrapingError(Exception):
    """Custom exception for scraping failures."""

    pass


def scrape_h2_tags_from_webscraper_io():
    """
    Scrapes H2 tags from https://webscraper.io/test-sites/tables.
    Returns a JSON string of H2 tags on success.
    Raises ScrapingError on failure.
    Informational messages are printed to stderr.
    """
    if is_running_in_docker():
        logger.info("INFO: main.py - Determined running in Docker environment.")
    else:
        logger.info("INFO: main.py - Determined running in local environment.")

    driver = None
    try:
        logger.info("INFO: Setting up Chrome WebDriver using utils configuration...")
        driver = webdriver.Chrome(
            service=get_chrome_service(), options=get_chrome_options()
        )
        logger.info("INFO: WebDriver setup complete.")

        url = "https://webscraper.io/test-sites/tables"
        logger.info(f"INFO: Navigating to {url}...")
        driver.get(url)
        logger.info(f"INFO: Page '{driver.title}' loaded successfully.")

        logger.info("INFO: Finding H2 elements...")
        h2_elements = driver.find_elements(By.TAG_NAME, "h2")
        logger.info(f"INFO: Found {len(h2_elements)} H2 elements.")

        logger.info(f"\n--- H2 Tags from {url} (Info) ---")
        if h2_elements:
            for index, h2 in enumerate(h2_elements):
                logger.info(f"{index + 1}. {h2.text.strip()}")
        else:
            logger.info("No H2 tags found on the page.")
        logger.info("\n--- End of H2 Tags (Info) ---")

        return json.dumps({"h2_tags": [h2.text.strip() for h2 in h2_elements]})

    except Exception as e:
        logger.error(
            f"ERROR: An internal error occurred during the scraping process: {e}"
        )
        raise ScrapingError(
            f"Failed to scrape H2 tags due to an internal error: {e}"
        ) from e
    finally:
        if driver:
            logger.info("INFO: Closing WebDriver.")
            driver.quit()
            logger.info("INFO: WebDriver closed.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    try:
        json_output = scrape_h2_tags_from_webscraper_io()
        print(json_output)
    except ScrapingError as se:
        logger.error(f"Scraping failed: {se}")
        sys.exit(1)
    except Exception as e:
        logger.critical(
            f"An unexpected error occurred in main execution: {e}", exc_info=True
        )
        sys.exit(1)
