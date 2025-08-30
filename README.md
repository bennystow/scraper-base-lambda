A base template for creating and deploying Python web scrapers on AWS Lambda using Docker.

## Table of Contents

- Prerequisites
- Getting Started
- Docker Usage
- Pre-commit Hooks
- Deployment
- TODO

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.12+
- Docker
- AWS CLI (optional, for manual deployment)

## Getting Started

Follow these steps to get your local development environment set up.

### 1. Clone the Repository

```sh
git clone <your-repository-url>
cd <repository-directory>
```

### 2. Create and Activate Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

**On Windows:**
```shell
python -m venv .venv
.\.venv\Scripts\activate
```

**On macOS/Linux:**
```shell
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages.
```shell
pip install -e .
```

### 4. Run the Application

Execute the main script to run the scraper locally.
```shell
python -m src.main
```

## Pre-commit Hooks

This project uses pre-commit hooks to enforce code quality and consistency. The following hooks are used:

- **check-yaml**: Checks yaml files for parseable syntax.
- **check-merge-conflict**: Checks for files that contain merge conflict strings.
- **end-of-file-fixer**: Ensures that a file is either empty, or ends with one newline.
- **trailing-whitespace**: Trims trailing whitespace.
- **ruff**: An extremely fast Python linter, written in Rust. Used for linting.
- **ruff-format**: The Ruff Formatter. Used for code formatting.
- **safety**: Checks your installed dependencies for known security vulnerabilities.

### 1. Install pre-commit

```shell
pip install pre-commit
```

### 2. Install the hooks

```shell
pre-commit install
```

Now, the hooks will run automatically before each commit. You can also run them manually at any time:

```shell
pre-commit run --all-files
```

## Docker Usage

You can also build and run this project as a Docker container.

### Build the Image

Build the Docker image using the provided `Dockerfile`.
```shell
docker build -t aws-lambda-base-selenium-scraper .
```

### Run the Container

Run the container, passing the handler location as an argument. This will execute the scraper inside the isolated Docker environment. Based on the local run command (`python -m src.main`), the handler is likely `src.main.handler`.

```shell
docker run -p 9000:8080 --rm aws-lambda-base-selenium-scraper src.main.handler
```

Once the container is running, you can invoke the function in a separate terminal by sending a POST request to the runtime interface emulator:

```shell
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```
*(Note: You might need to pass environment variables for configuration, e.g., `docker run --rm -e VAR=value aws-lambda-base-selenium-scraper`)*

## Deployment

This project is set up for continuous deployment to AWS Lambda via GitHub Actions.

The deployment workflow is defined in `.github/workflows/deploy.yml`. This workflow will typically:
1.  Build the Docker image.
2.  Push the image to Amazon ECR (Elastic Container Registry).
3.  Update the AWS Lambda function to use the new container image.

Please review and configure the workflow file with your specific AWS details (e.g., ECR repository name, AWS region, IAM role).

## TODO

- [ ] Update `.github/workflows/deploy.yml` to work correctly with your AWS environment.
