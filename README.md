
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

# LogX Dashboard

A full-stack log analytics and visualization platform built with Flask, Streamlit, Dash, and supporting AWS Lambda for log parsing. The project enables ingestion, search, and visualization of logs from various sources.

---

## Project Structure

```
Logs-project/
│
├── api/                # Flask REST API for log search and stats
│   ├── Dockerfile
│   ├── requirements.txt
│   └── search_api.py
│
├── dashboard/          # Streamlit & Dash dashboard for log analytics
│   ├── app.py
│   ├── requirements.txt
│   └── ...
│
├── lambda/             # AWS Lambda log parser
│   ├── log_parser.py
│   └── requirements.txt
│
├── scripts/            # Utility scripts (e.g., log generator)
│   └── log_generator.py
│
├── tests/              # Unit tests
│   ├── test_api.py
│   └── test_parser.py
│
├── docker-compose.yml  # (Optional) For multi-service orchestration
└── README.md           # Project documentation
```

---

## Features

- **Log Ingestion & Search:** REST API for searching and aggregating logs.
- **Dashboard:** Interactive analytics dashboard with filters, charts, and log timeline.
- **AWS Lambda Integration:** For scalable log parsing and ingestion.
- **Dockerized:** Easy deployment using Docker.
- **Custom Filters:** Filter logs by time, level, source, and search query.
- **Auto-refresh:** Option to auto-refresh dashboard data.

---

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/Logs-project.git
cd Logs-project
```

### 2. Build and Run the API Service

```sh
cd api
pip install -r requirements.txt
python search_api.py
```
Or with Docker:
```sh
docker build -t logs-api .
docker run -p 5000:5000 logs-api
```

### 3. Build and Run the Dashboard

```sh
cd ../dashboard
pip install -r requirements.txt
streamlit run app.py
```
- The dashboard will be available at [http://localhost:8501](http://localhost:8501).

### 4. (Optional) Run Lambda Parser

```sh
cd ../lambda
pip install -r requirements.txt
python log_parser.py
```

---

## Configuration

- **API Endpoint:**  
  The dashboard expects the API to be available at `http://localhost:5000/api`.  
  Update `API_BASE_URL` in `dashboard/app.py` if your API runs elsewhere.

- **Ports:**  
  - API: `5000`
  - Dashboard: `8501` (Streamlit default)

---

## Usage

- **Open the dashboard** in your browser.
- **Apply filters** (time range, log level, source, search query).
- **View analytics**: log timeline, source distribution, log level distribution, and recent logs.
- **Logs API**: Use `/api/search` and `/api/stats` endpoints for programmatic access.

---

## Logging & Monitoring

- **API logs**: Output to terminal or log file (if configured).
- **Dashboard logs**: Output to terminal running Streamlit.
- **AWS CloudWatch**: (Optional) Configure CloudWatch agent for centralized log monitoring.

---

## Troubleshooting

- **Dashboard shows connection error:**  
  Ensure the API service is running and accessible at the configured URL/port.

- **ModuleNotFoundError:**  
  Double-check all dependencies are installed using the provided `requirements.txt`.

- **Port conflicts:**  
  Make sure required ports (5000, 8501) are free or update the code/config to use different ports.

---

## License

MIT License

---