# LogX - Serverless Real-Time Log Analysis Platform

## Quick Start

### Prerequisites
- AWS CLI configured
- Terraform >= 1.0
- Python 3.9+
- Docker
- Node.js (for dashboard)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd logx-serverless
```

### 2. Install Dependencies
- For Lambda functions:
  ```bash
  cd lambda
  pip install -r requirements.txt
  ```
- For API:
  ```bash
  cd api
  pip install -r requirements.txt
  ```
- For Dashboard:
  ```bash
  cd dashboard
  npm install
  ```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add the following variables:
```
AWS_REGION=<your-aws-region>
KINESIS_STREAM_NAME=<your-kinesis-stream-name>
LAMBDA_FUNCTION_NAME=<your-lambda-function-name>
OPENSEARCH_ENDPOINT=<your-opensearch-endpoint>
API_GATEWAY_ENDPOINT=<your-api-gateway-endpoint>
```

### 4. Deploy Infrastructure
Use Terraform to deploy the infrastructure:
```bash
cd terraform
terraform init
terraform apply
```

### 5. Build and Run Dashboard
```bash
cd dashboard
npm run build
npm start
```

## Project Structure
The project is organized into several directories, each serving a specific purpose:

- **lambda/**: Contains the logic for parsing logs.
  - `log_parser.py`: Implements functions to read and process log files.
  - `requirements.txt`: Lists the dependencies required for the Lambda functions.
  - `__init__.py`: Marks the directory as a Python package.

- **api/**: Implements the API for searching logs.
  - `search_api.py`: Handles incoming requests and queries log data.
  - `requirements.txt`: Lists the dependencies required for the API.
  - `Dockerfile`: Contains instructions to build a Docker image for the API service.

- **terraform/**: Contains Terraform configuration files for infrastructure setup.
  - `main.tf`: Main configuration file for defining AWS resources.
  - `kinesis.tf`: Configuration for AWS Kinesis.
  - `lambda.tf`: Configuration for AWS Lambda functions.
  - `opensearch.tf`: Configuration for AWS OpenSearch.
  - `api_gateway.tf`: Configuration for AWS API Gateway.
  - `variables.tf`: Defines variables used in the Terraform configurations.

- **dashboard/**: Contains the dashboard application for displaying logs.
  - `app.py`: Entry point for the dashboard application.
  - `requirements.txt`: Lists the dependencies required for the dashboard.

- **scripts/**: Contains utility scripts.
  - `log_generator.py`: Script to generate log data for testing or demonstration.

- **tests/**: Contains unit tests for the project.
  - `test_parser.py`: Unit tests for the log_parser module.
  - `test_api.py`: Unit tests for the search_api module.

- **.github/workflows/**: Contains GitHub Actions workflows for deployment.
  - `deploy.yml`: Defines the steps for building and deploying the project.

- **docker-compose.yml**: Defines services, networks, and volumes for running the application using Docker Compose.

- **Jenkinsfile**: Configuration for Jenkins CI/CD, specifying build, test, and deployment steps.

## Usage
- Access the API at the specified endpoint to search logs.
- Use the dashboard to visualize and interact with log data.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.