\# 🛒 E-Commerce ETL \& Analytics Pipeline



An end-to-end data engineering project that simulates an e-commerce data platform and processes transactional data through a complete ETL pipeline using \*\*Python, PySpark, PostgreSQL, Apache Airflow, and Streamlit\*\*.



The project generates realistic e-commerce data, introduces intentional data-quality issues, cleans and transforms the data using PySpark, loads it into PostgreSQL, builds an analytical data model, orchestrates the workflow with Airflow, and exposes business insights through an interactive Streamlit dashboard.



\---



\## 🚀 Project Overview



This project demonstrates a production-style batch data engineering workflow:



```text

Synthetic E-Commerce Data

&#x20;         │

&#x20;         ▼

&#x20;    Python / Faker

&#x20;         │

&#x20;         ▼

&#x20;     Raw CSV Files

&#x20;         │

&#x20;         ▼

&#x20;      PySpark

&#x20;  Data Cleaning \& QA

&#x20;         │

&#x20;         ▼

&#x20;   Processed Parquet

&#x20;         │

&#x20;         ▼

&#x20;     PostgreSQL

&#x20;  ┌───────────────┐

&#x20;  │   Staging     │

&#x20;  │   Analytics   │

&#x20;  └───────────────┘

&#x20;         │

&#x20;         ▼

&#x20;  Analytics Views

&#x20;         │

&#x20;         ▼

&#x20;     Streamlit

&#x20;     Dashboard



🧰 Tech Stack

Technology	Purpose

Python	Data generation and pipeline logic

Faker	Synthetic e-commerce data generation

PySpark	Data cleaning and transformation

Parquet	Processed data storage

PostgreSQL	Data warehouse / analytical database

Apache Airflow	ETL orchestration

Streamlit	Interactive analytics dashboard

Plotly	Data visualization

Docker	Containerized PostgreSQL and Airflow

Git	Version control

📊 Dataset



The pipeline generates five datasets:



Customers



Contains customer information.



Customer ID

Name

Email

Phone

Registration date

City

Country

Products



Contains product catalog information.



Product ID

Product name

Category

Price

Orders



Contains customer order information.



Order ID

Customer ID

Order date

Order status

Total amount

Order Items



Contains individual products within each order.



Order item ID

Order ID

Product ID

Quantity

Unit price

Line total

Payments



Contains payment information.



Payment ID

Order ID

Payment date

Payment method

Payment status

🧪 Intentional Data Quality Issues



The generated dataset intentionally contains data-quality problems to demonstrate real-world ETL processing.



Customers

Duplicate customer records

Missing email addresses

Invalid email formats

Order Items

Invalid quantities such as 0

Orders

Different order statuses

Cancelled orders without payments



Cancelled orders without payments are treated as valid business scenarios rather than data-quality errors.



🔍 Data Quality Checks



The pipeline performs checks including:



Duplicate customer IDs

Missing emails

Invalid email formats

Invalid quantities

Invalid prices

Referential integrity

Orders without payments

Payment status distribution



Example payment distribution from the generated dataset:



Success : 3,293

Failed  : 1,139



The generated data is synthetic and may change when the pipeline is executed again.



🧹 PySpark Data Cleaning



The raw CSV data is processed using PySpark.



Customer cleaning

Remove duplicate customer IDs

Normalize email values

Convert invalid email addresses to NULL

Order item cleaning



Rows with:



quantity <= 0



are removed.



Business rule



Cancelled orders without payments are retained because they represent a valid business scenario.



🗄️ PostgreSQL Data Model



The PostgreSQL database contains two major layers.



Staging

staging.customers

staging.products

staging.orders

staging.order\_items

staging.payments



The staging layer stores cleaned transactional data before analytical transformation.



⭐ Analytics Model



The analytical layer follows a simplified dimensional model.



Dimension Tables

analytics.dim\_customers

analytics.dim\_products

Fact Tables

analytics.fact\_orders

analytics.fact\_order\_items



This structure supports analytical queries while separating descriptive dimensions from transactional facts.



📈 Analytics Views



The project provides analytical views for the dashboard.



analytics.v\_daily\_sales

analytics.v\_category\_sales

analytics.v\_product\_sales



These views provide:



Daily revenue

Daily order counts

Units sold

Category revenue

Category order counts

Product revenue



Cancelled orders are excluded from revenue-oriented analytical views.



🔄 Apache Airflow Pipeline



The entire ETL workflow is orchestrated using Apache Airflow.



DAG

ecommerce\_etl

Tasks

generate\_data

&#x20;     ↓

clean\_data\_with\_pyspark

&#x20;     ↓

load\_parquet\_to\_postgres

&#x20;     ↓

transform\_analytics

&#x20;     ↓

create\_dashboard\_views



The DAG is configured for daily execution.



⚙️ Airflow Environment



Airflow runs using Docker with:



Apache Airflow 2.10.5

PostgreSQL metadata database

LocalExecutor

OpenJDK 17

PySpark 4.2.0

pandas

PyArrow

psycopg2

Faker

📊 Streamlit Dashboard



The project includes an interactive Streamlit dashboard.



Dashboard KPIs

Total Orders

Completed Orders

Cancelled Orders

Revenue

Average Order Value

Visualizations

Revenue by category

Units sold by category

Daily revenue trend

Order status distribution

Top 10 products by revenue

Category performance table

Filters



Users can filter the dashboard by product category.



✅ Pipeline Validation



The pipeline was validated using independent revenue calculations.



The revenue calculated from the category analytics view:



₹918,723,381.34



matches the revenue independently calculated from the fact table:



₹918,723,381.34



Difference:



₹0.00



This validates the consistency between the analytical view and the underlying fact table.



📌 Example Dataset Metrics



One successful pipeline run produced:



Customers       : 1,000

Products        : 200

Orders          : 5,000

Order Items     : 14,923

Payments        : 4,432



Example order-status distribution:



Completed       : 2,526

Cancelled       :   828

Processing      :   824

Shipped         :   822



Because the pipeline generates synthetic data, these values can change when the pipeline is executed again.



📁 Project Structure

E-commerce ETL Pipeline/

│

├── dags/

│   └── ecommerce\_etl.py

│

├── data/

│   ├── raw/

│   └── processed/

│

├── hadoop/

│   └── bin/

│       ├── hadoop.dll

│       ├── hdfs.dll

│       └── winutils.exe

│

├── notebooks/

│

├── sql/

│   ├── staging/

│   │   ├── 01\_create\_schemas.sql

│   │   └── 02\_create\_staging\_tables.sql

│   │

│   └── analytics/

│       ├── 01\_create\_analytics\_tables.sql

│       ├── 02\_transform\_analytics.sql

│       ├── 03\_business\_queries.sql

│       └── 04\_dashboard\_views.sql

│

├── src/

│   ├── dashboard/

│   │   └── app.py

│   │

│   ├── ingestion/

│   │

│   ├── loading/

│   │   └── load\_to\_postgres.py

│   │

│   ├── transformations/

│   │   └── clean\_data.py

│   │

│   ├── data\_quality.py

│   ├── profiling.py

│   └── generate\_data.py

│

├── tests/

│

├── Dockerfile.airflow

├── docker-compose.airflow.yml

├── requirements.txt

├── .gitignore

└── README.md

🐳 Docker Services



The project uses Docker for PostgreSQL and Airflow.



PostgreSQL

Database : ecommerce

User     : etl\_user

Port     : 5432

Airflow

Web UI : http://localhost:8080



Airflow credentials for the local development environment:



Username : admin

Password : admin



These credentials are intended only for local development.



⚙️ Local Setup



1\. Clone the repository

git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

cd E-commerce-ETL-Pipeline

2\. Create a Python virtual environment

python -m venv .venv



Activate it:



.\\.venv\\Scripts\\Activate.ps1

3\. Install dependencies

pip install -r requirements.txt

🐘 PostgreSQL Setup



Start the PostgreSQL container.



docker start ecommerce-postgres



Verify:



docker ps



Test PostgreSQL:



docker exec ecommerce-postgres pg\_isready -U etl\_user -d ecommerce

✈️ Start Airflow



Build the Airflow image:



docker compose -f docker-compose.airflow.yml build



Start Airflow:



docker compose -f docker-compose.airflow.yml up -d



Open:



http://localhost:8080



Login using the local development credentials configured in the Compose file.



▶️ Run the ETL Pipeline



The Airflow DAG:



ecommerce\_etl



can be triggered from the Airflow UI.



Pipeline:



Generate Data

&#x20;     ↓

PySpark Cleaning

&#x20;     ↓

Load to PostgreSQL

&#x20;     ↓

Transform Analytics

&#x20;     ↓

Create Dashboard Views



📊 Run the Dashboard



From the project root:



streamlit run src\\dashboard\\app.py



Open:



http://localhost:8501



🔐 Configuration



Database settings can be configured through environment variables:



PGHOST

PGPORT

PGDATABASE

PGUSER

PGPASSWORD



Default local-development values are configured in the application.



For production deployments, credentials should be supplied through environment variables or a secrets manager rather than committed to source control.



🧠 Key Data Engineering Concepts Demonstrated



This project demonstrates practical experience with:



Batch ETL pipelines

Data ingestion

Data profiling

Data-quality validation

Data cleaning

PySpark transformations

Parquet

PostgreSQL

Dimensional modeling

Fact and dimension tables

Analytical SQL

SQL views

Workflow orchestration

Apache Airflow

Docker

Streamlit

Plotly

Data validation

Business analytics





🔮 Future Improvements



Potential future enhancements include:



Incremental data loading

Slowly Changing Dimensions

Cloud deployment on GCP

BigQuery integration

Cloud Storage data lake

Pub/Sub streaming ingestion

Data quality framework integration

Great Expectations

dbt transformations

CI/CD pipeline

Automated unit and integration tests

Authentication for the dashboard

Production secrets management

Monitoring and alerting



👨‍💻 Author



Peruri Subhash



Data Engineer | GCP | PySpark | SQL | Airflow



Interested in building scalable data pipelines, analytics systems, and cloud-based data engineering solutions.



⭐ Project Highlights

Python

&#x20;  +

PySpark

&#x20;  +

PostgreSQL

&#x20;  +

Apache Airflow

&#x20;  +

Docker

&#x20;  +

Streamlit



