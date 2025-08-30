import os
import logging
from tempfile import mkdtemp
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)


def is_running_in_docker():
    in_docker = os.environ.get("RUNNING_IN_DOCKER", "").lower() in ("true", "1")
    in_ci = os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
    return in_docker or in_ci


def get_chrome_options(headless_override=None):
    """
    Returns Chrome options suitable for the current environment (local or Docker).
    Args:
    headless_override (bool, optional): If True, forces headless mode.
        If False, forces non-headless mode.
        If None, determines headless based on environment.
        Defaults to None.
    """
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    run_headless = (
        headless_override if headless_override is not None else is_running_in_docker()
    )

    if run_headless:
        logger.info("Applying headless Chrome options.")

        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"
    else:
        logger.info("Applying non-headless Chrome options.")

    return chrome_options


def get_chrome_service(headless_override=None):
    if is_running_in_docker():
        logger.info("SERVICE - Running in Docker environment")
        return Service(
            executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
            service_log_path="/tmp/chromedriver.log",
        )

    else:
        logger.info("SERVICE - Running in local environment")
        return None
