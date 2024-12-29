# Redfin Data Analytics End-To-End Python ETL Pipeline

## Overview

This project involves creating an **end-to-end ETL (Extract, Transform, Load)** pipeline to process real estate data from the **Redfin API**. The pipeline is designed to extract raw data from Redfin, transform it for analytical purposes, and load it into an **Amazon Redshift** data warehouse. The solution is fully automated using **Docker**, **Apache Airflow** (with **Astronomer** for orchestration), **AWS Lambda**, and **Amazon S3**, providing a scalable and efficient workflow for real-time analytics.

### Architectural Diagram

![Project Architecture](./assets/architectural%20diagram.jpg)

The architecture includes the following components:

- **Redfin API**: Source of raw real estate data.
- **Amazon S3 (Raw and Transformed Buckets)**: Used for storing raw and transformed data.
- **AWS Lambda**: Used for transforming the raw data.
- **Amazon Redshift**: Data warehouse for storing structured, analytical data.
- **Apache Airflow (via Astronomer)**: Used to orchestrate and manage the ETL tasks.
- **Docker**: For containerizing the pipeline components.

---

## Project Workflow

### Step 1: Extraction from Redfin API
**Goal**: Fetch raw real estate data from the Redfin API and store it in an Amazon S3 raw data bucket.

**Implementation**:
- Developed a **Python script** to connect to the **Redfin API** via HTTP requests and extract data.
- Used **Apache Airflow** (running via **Astronomer**) to schedule and manage the API calls at regular intervals.
- Stored the fetched data (in **JSON** or **CSV** format) to an **S3 bucket** named `s3://redfin-raw-data`.
- Incorporated logging and error handling to track API request statuses and manage rate-limiting.

### Step 2: Data Transformation with AWS Lambda
**Goal**: Transform the raw data into an analytics-ready format.

**Implementation**:
- Built an **AWS Lambda function** triggered by the `s3:ObjectCreated` event in the raw S3 bucket.
- The Lambda function:
  - Reads raw data files from S3.
  - Cleans and preprocesses the data, such as handling missing values and standardizing field names.
  - Adds new features like **price per square foot** for enhanced analysis.
  - Saves the transformed data to a different S3 bucket: `s3://redfin-transformed-data`.
- Set up **AWS CloudWatch** for monitoring Lambda execution and error alerts.

### Step 3: Data Load into Amazon Redshift
**Goal**: Load the transformed data from S3 into Amazon Redshift for further analysis.

**Implementation**:
- Created an **Airflow task** using the **S3KeySensor** to monitor the transformed data bucket.
- Once new transformed data is detected, the task triggers the **Redshift COPY** command to load data into a staging table.
- Applied **SQL transformations** in Redshift to move data from staging tables to final analytical tables for reporting and querying.
- Implemented error handling and automated retry logic during the loading process.

### Step 4: Orchestration with Apache Airflow (via Astronomer)
**Goal**: Orchestrate the entire ETL pipeline and manage task dependencies.

**Implementation**:
- Designed a modular **Airflow DAG** to automate the pipeline:
  - **Extract**: Fetch raw data from Redfin API and store it in the raw S3 bucket.
  - **Transform**: Trigger Lambda to process the raw data.
  - **Sensor**: Use **S3KeySensor** to detect transformed data in the transformed S3 bucket.
  - **Load**: Load the transformed data into Redshift for analysis.
- Set up **periodic scheduling** (daily or as required) to automate the ETL process.
- Utilized **Astronomer** (a cloud-native platform for Apache Airflow) to streamline deployment, management, and scaling of Airflow.

### Step 5: Dockerization for Containerization
**Goal**: Package the pipeline components into Docker containers for portability, scalability, and ease of deployment.

**Implementation**:
- Containerized the **Airflow environment** and necessary **Python scripts** (for Redfin API extraction and Lambda simulation).
- Created a **Dockerfile** to install dependencies, set up Airflow, and configure the environment for local testing and deployment.
- Integrated **Docker Compose** to manage multiple containers (Airflow, PostgreSQL for Airflow metadata, etc.).
- Ensured that the pipeline can run consistently across different platforms (local development, staging, production).

---

## Key Achievements

- **Full Automation**: The entire data extraction, transformation, and loading process is automated, significantly reducing manual intervention.
- **Scalability**: The pipeline is designed to scale and handle large datasets, making it future-proof for increased data volumes.
- **Portability**: The pipeline is dockerized, ensuring that the environment can be easily replicated or deployed on any platform supporting Docker.
- **Cloud-Native Orchestration**: Utilized **Astronomer** to manage and deploy **Apache Airflow**, providing a streamlined, efficient environment for workflow orchestration.
- **Data Quality**: Implemented rigorous **data transformation** processes to ensure the quality and accuracy of data for reporting and analysis.
- **Analytics-Ready Data**: The pipeline provides stakeholders with structured, cleaned, and ready-to-query data for **real-time business intelligence** and decision-making.

---

## Setup and Installation

### Requirements:
- **Docker**
- **Python 3.x**
- **AWS Account** (with access to S3, Lambda, and Redshift)
- **Astronomer** account for managing Apache Airflow

### Steps:

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/redfin-etl-pipeline.git
   cd redfin-etl-pipeline
