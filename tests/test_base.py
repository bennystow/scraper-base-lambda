import unittest
import subprocess
import json
import os

# Define the image name, assuming it's built as 'base-lambda-scraper'
DOCKER_IMAGE_NAME = "aws-lambda-base-selenium-scraper"


class TestScrapingLogic(unittest.TestCase):
    @classmethod  # This setup might still be useful for other tests that DO run the container
    def setUpClass(cls):
        """
        Build the Docker image once before all tests in this class.
        This ensures that any changes to the source code are included.
        Docker's layer caching makes this efficient.
        """
        dockerfile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        print(f"Building Docker image: {DOCKER_IMAGE_NAME} from {dockerfile_dir}")
        try:
            subprocess.run(
                ["docker", "build", "-t", DOCKER_IMAGE_NAME, "."],
                cwd=dockerfile_dir,  # Run docker build from the directory containing the Dockerfile
                check=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout for build
            )
            print("Docker image build successful.")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            # If the build fails, we want to see the error and stop the tests.
            print("Docker build failed.")
            # stdout and stderr are attributes on the exception object itself
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise

    def test_docker_run_produces_valid_json_with_h2_tags(self):
        """
        Tests that running the main script inside the Docker container
        produces a valid JSON output on stdout with the 'h2_tags' key.
        This is an integration test.
        """
        print(f"\nRunning Docker container {DOCKER_IMAGE_NAME} to test output...")
        try:
            # The command to run inside the container is defined by the Dockerfile's CMD.
            # We assume it's `["python", "src/main.py"]`.
            # The `--rm` flag ensures the container is removed after it exits.
            result = subprocess.run(
                ["docker", "run", "--rm", DOCKER_IMAGE_NAME],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,  # 60-second timeout for the container to run and exit
            )

            # In main.py, JSON output is sent to stdout via print()
            stdout = result.stdout.strip()
            self.assertTrue(stdout, "STDOUT from container was empty.")

            # 2. Check if it's valid JSON and has the 'h2_tags' key
            try:
                data = json.loads(stdout)
                self.assertIn(
                    "h2_tags", data, "The returned JSON must have an 'h2_tags' key."
                )
                self.assertIsInstance(
                    data["h2_tags"],
                    list,
                    "The 'h2_tags' key should correspond to a list.",
                )
            except json.JSONDecodeError as e:
                self.fail(
                    f"The function did not return a valid JSON string. Error: {e}\nOutput was: '{stdout}'"
                )

        except subprocess.CalledProcessError as e:
            self.fail(
                f"Docker container exited with an error.\n"
                f"Exit Code: {e.returncode}\n"
                f"STDOUT: {e.stdout}\n"
                f"STDERR: {e.stderr}"
            )
        except Exception as e:
            self.fail(f"An unexpected error occurred during the test: {e}")


if __name__ == "__main__":
    unittest.main()
