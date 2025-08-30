import json
import unittest
from unittest.mock import patch

from src.main import handler

# Define the image name, assuming it's built as 'base-lambda-scraper'
DOCKER_IMAGE_NAME = "aws-lambda-base-selenium-scraper"


# class TestLambdaScraperIntegration(unittest.TestCase):
#     """
#     Integration tests for the Lambda scraper function running in a Docker container.
#     """

#     container_name = f"{DOCKER_IMAGE_NAME}-test-container"
#     container_id = None
#     host_port = 9000
#     base_url = f"http://localhost:{host_port}"

#     @classmethod  # This setup might still be useful for other tests that DO run the container
#     def setUpClass(cls):
#         """
#         Build the Docker image once before all tests in this class.
#         This ensures that any changes to the source code are included.
#         Docker's layer caching makes this efficient.
#         """
#         dockerfile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
#         print(f"Building Docker image: {DOCKER_IMAGE_NAME} from {dockerfile_dir}")
#         try:
#             subprocess.run(
#                 ["docker", "build", "-t", DOCKER_IMAGE_NAME, "."],
#                 cwd=dockerfile_dir,  # Run docker build from the directory containing the Dockerfile
#                 check=True,
#                 capture_output=True,
#                 text=True,
#                 timeout=300,  # 5 minutes timeout for build
#             )
#             print("Docker image build successful.")
#         except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
#             # If the build fails, we want to see the error and stop the tests.
#             print("Docker build failed.")
#             # stdout and stderr are attributes on the exception object itself
#             print(f"STDOUT: {e.stdout}")
#             print(f"STDERR: {e.stderr}")
#             raise

#     def setUp(self):
#         """
#         Start the Docker container before each test.
#         """
#         print(f"\nStarting Docker container {self.container_name}...")
#         try:
#             # Ensure no old container with the same name exists
#             subprocess.run(
#                 ["docker", "rm", "-f", self.container_name],
#                 capture_output=True,
#                 check=False,
#             )

#             run_cmd = [
#                 "docker",
#                 "run",
#                 "-d",
#                 "-p",
#                 f"{self.host_port}:8080",
#                 "--shm-size=2g",  # Increase shared memory for Chrome, a common fix for startup issues
#                 "-e",
#                 "_HANDLER=src.main.handler",  # Explicitly set the handler env var for the runtime
#                 "--name",
#                 self.container_name,
#                 DOCKER_IMAGE_NAME,
#             ]
#             self.container_id = (
#                 subprocess.check_output(run_cmd).decode("utf-8").strip()
#             )
#             self._wait_for_lambda_ready()  # Will now use a longer timeout and provide logs on failure
#             print(f"Container {self.container_id[:12]} started.")
#         except Exception as e:
#             # If setUp fails, tearDown will be called automatically by unittest runner.
#             self.fail(f"Failed to start and prepare Docker container: {e}")

#     def tearDown(self):
#         """
#         Stop and remove the Docker container after each test.
#         """
#         if self.container_id:
#             print(f"\nStopping and removing container {self.container_id[:12]}...")
#             subprocess.run(
#                 ["docker", "stop", self.container_id], capture_output=True, check=False
#             )
#             # rm by name is safer in case id was not captured correctly but container is running
#             subprocess.run(
#                 ["docker", "rm", self.container_name], capture_output=True, check=False
#             )
#             self.container_id = None

#     def _wait_for_lambda_ready(self, timeout=40):
#         """
#         Polls the Lambda RIE to ensure it's ready to accept invocations.
#         """
#         print("Waiting for Lambda RIE to be ready...")
#         start_time = time.time()
#         ping_url = f"{self.base_url}/2018-06-01/ping"
#         while time.time() - start_time < timeout:
#             try:
#                 with urllib.request.urlopen(ping_url, timeout=1) as response:
#                     if response.getcode() == 200:
#                         print("Lambda RIE is ready.")
#                         return
#             except (urllib.error.URLError, ConnectionRefusedError):
#                 # Check if the container is still running. If not, it likely crashed.
#                 container_state_result = subprocess.run(
#                     ["docker", "inspect", "-f", "{{.State.Status}}", self.container_name],
#                     capture_output=True, text=True, check=False
#                 )
#                 if container_state_result.returncode != 0 or container_state_result.stdout.strip() != "running":
#                     break  # Exit the loop early if container has stopped or doesn't exist
#                 time.sleep(1)

#         # If we time out or the container crashed, get the logs before failing.
#         logs_result = subprocess.run(
#             ["docker", "logs", self.container_name],
#             capture_output=True,
#             text=True,
#             check=False,
#         )
#         logs = logs_result.stdout or logs_result.stderr

#         self.fail(
#             f"Lambda RIE did not become ready in {timeout} seconds.\n"
#             f"Container logs:\n---\n{logs}\n---"
#         )

#     def test_handler_returns_h2_tags_in_json(self):
#         """
#         Tests that invoking the Lambda handler returns a valid JSON response
#         containing a non-empty list of h2 tags.
#         """
#         print("Invoking Lambda function...")
#         url = f"{self.base_url}/2015-03-31/functions/function/invocations"
#         # The event payload is empty, as the handler is expected to have a default URL to scrape.
#         req = urllib.request.Request(
#             url,
#             data=b"{}",
#             method="POST",
#             headers={"Content-Type": "application/json"},
#         )

#         try:
#             with urllib.request.urlopen(req, timeout=60) as response:
#                 self.assertEqual(
#                     response.getcode(),
#                     200,
#                     "Expected a 200 OK response from the Lambda invocation.",
#                 )
#                 response_body = response.read()
#         except urllib.error.URLError as e:
#             self.fail(f"Failed to invoke lambda via RIE: {e}")

#         # The response from RIE is a JSON object containing the lambda's response
#         lambda_response = json.loads(response_body)

#         self.assertEqual(
#             lambda_response.get("statusCode"),
#             200,
#             f"Lambda function should return statusCode 200. Response: {lambda_response}",
#         )
#         body_str = lambda_response.get("body")
#         self.assertTrue(body_str, "Body from lambda response was empty.")

#         # The body is a JSON string, so we need to parse it
#         try:
#             data = json.loads(body_str)
#             self.assertIn(
#                 "h2_tags", data, "The returned JSON must have an 'h2_tags' key."
#             )
#             self.assertIsInstance(
#                 data["h2_tags"],
#                 list,
#                 "The 'h2_tags' key should correspond to a list.",
#             )
#             # A basic check that we got some tags. This assumes the target page has h2 tags.
#             self.assertTrue(
#                 len(data["h2_tags"]) > 0, "The 'h2_tags' list should not be empty."
#             )
#             expected_h2_tags = [
#                 "Table playground",
#                 "Semantically correct table with thead and tbody",
#             ]
#             self.assertListEqual(
#                 data["h2_tags"],
#                 expected_h2_tags,
#                 "The scraped h2 tags do not match the expected content.",
#             )
#             print(f"Successfully verified content of {len(data['h2_tags'])} h2 tags.")
#         except json.JSONDecodeError as e:
#             self.fail(
#                 f"The handler did not return a valid JSON string in the body. Error: {e}\nBody was: '{body_str}'"
#             )
#         except Exception as e:
#             self.fail(f"An unexpected error occurred during response validation: {e}")


class TestHandlerLogic(unittest.TestCase):
    """
    Unit tests for the handler logic in src/main.py, mocking the scraper.
    These tests are fast and do not require Docker or a live network connection.
    """

    @patch("src.main.scrape_h2_tags_from_webscraper_io")
    def test_handler_returns_correct_json_on_success(self, mock_scrape):
        """
        Tests that the handler correctly formats a successful scraping result
        with the specific expected content.
        """
        # Arrange
        expected_h2_tags = [
            "Table playground",
            "Semantically correct table with thead and tbody",
        ]
        scraper_output = json.dumps({"h2_tags": expected_h2_tags})
        mock_scrape.return_value = scraper_output

        # Act
        response = handler(event={}, context={})

        # Assert
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"], {"Content-Type": "application/json"})
        response_body = json.loads(response["body"])
        self.assertIn("h2_tags", response_body)
        self.assertListEqual(response_body["h2_tags"], expected_h2_tags)
        mock_scrape.assert_called_once()


if __name__ == "__main__":
    unittest.main()
