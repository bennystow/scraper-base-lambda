import json
import logging
import sys

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


def handler(event, context):
    """
    AWS Lambda handler function.

    This function is the entry point for the AWS Lambda execution. It
    initializes logging, invokes the web scraper, and formats the output
    (or any errors) into the response format expected by API Gateway.

    :param event: The event dictionary passed by AWS Lambda.
    :param context: The context object passed by AWS Lambda.
    :return: A dictionary formatted for an API Gateway proxy response.
    """
    # Lambda runtime configures a default logger. We can just use it.
    try:
        # The scraping function returns a JSON string
        result_json_string = scrape_h2_tags_from_webscraper_io()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result_json_string,
        }
    except ScrapingError as e:
        logger.error(f"A scraping error occurred: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": "Scraping failed", "details": str(e)})}
    except Exception as e:
        logger.critical(f"An unexpected error occurred in handler: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "An internal server error occurred.", "details": str(e)}),
        }


def scrape_h2_tags_from_webscraper_io():
    """
    Scrapes H2 tags from https://webscraper.io/test-sites/tables.
    Returns a JSON string of H2 tags on success.
    Raises ScrapingError on failure.
    Informational messages are printed to stderr.
    """
    if is_running_in_docker():
        logger.info("Determined running in Docker environment.")
    else:
        logger.info("Determined running in local environment.")

    driver = None
    try:
        logger.info("Setting up Chrome WebDriver using utils configuration...")
        driver = webdriver.Chrome(service=get_chrome_service(), options=get_chrome_options())
        logger.info("WebDriver setup complete.")

        url = "https://webscraper.io/test-sites/tables"
        logger.info(f"Navigating to {url}...")
        driver.get(url)
        logger.info(f"Page '{driver.title}' loaded successfully.")

        logger.info("Finding H2 elements...")
        h2_elements = driver.find_elements(By.TAG_NAME, "h2")
        logger.info(f"Found {len(h2_elements)} H2 elements.")

        logger.info(f"--- H2 Tags from {url} ---")
        if h2_elements:
            for index, h2 in enumerate(h2_elements):
                logger.info(f"{index + 1}. {h2.text.strip()}")
        else:
            logger.info("No H2 tags found on the page.")
        logger.info("--- End of H2 Tags ---")

        return json.dumps({"h2_tags": [h2.text.strip() for h2 in h2_elements]})

    except Exception as e:
        logger.error(f"An internal error occurred during the scraping process: {e}")
        raise ScrapingError(f"Failed to scrape H2 tags due to an internal error: {e}") from e
    finally:
        if driver:
            logger.info("Closing WebDriver.")
            driver.quit()
            logger.info("WebDriver closed.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    try:
        # Simulate a Lambda invocation
        response = handler(event={}, context={})
        # Pretty-print the JSON body of the response
        print(json.dumps(json.loads(response["body"]), indent=2))
        if response["statusCode"] != 200:
            sys.exit(1)
    except ScrapingError as se:
        logger.error(f"Scraping failed: {se}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred in main execution: {e}", exc_info=True)
        sys.exit(1)
