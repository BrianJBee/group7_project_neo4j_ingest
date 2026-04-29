# Group 7 Project - Neo4j Ingestion
## Abstract
This project designs a data pipeline for evaluating restaurant performance using the Yelp Open Dataset, which contains business, user, and review data. Raw JSON data, including user, business, and review information, is ingested into cloud storage and preprocessed to ensure compatibility with a structured query environment. The cleaned data is then loaded into a cloud-based data warehouse, where a transformation workflow is implemented using a layered approach consisting of staging, intermediate, and mart models. 

The final warehouse adopts a snowflake schema where the fact and dimension tables are constructed to enable insights into business performance, competition, and engagement trends. Additionally, the pipeline integrates version control for collaborative development and supports downstream analytics and visualization through dashboarding tools. This end-to-end system demonstrates how raw, semi-structured data can be transformed into a structured and query-optimized format for business intelligence applications.

## About This Repo
Instead of ingesting the raw JSON files, data is queried directly from BigQuery using the BigQuery Python driver and API, then merged into Neo4j as nodes and relationships (edges). Using a combination of these tools and some query optimizations in SQL, a subset of the data is queried and merged into the database, minimizing unnecessary computational and storage overhead while preserving useful analytics from top competitors.

## Setup
### 1. Create virtual environment:

Windows:
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
In order to ingest data to the target database, potentially sensitive data is used for authentication and remote connection. An example file `.env.example` is provided:  

**Create `.env`**
```bash
cp .env.example .env
```  

Or, manually create a `.env` file and copy the following:
```env
NEO_HOST=
NEO_PORT=
NEO_USER=
NEO_PASS=
```

Fill out `.env` according to your database specifications.  

*Note:* Do not share this file publicly, including committing to version control.  

### 4. Run `main.py` (As a Package)
```bash
cd src
python -m graph_analysis.main
```  
Leave this process running until the console prints `"Done!"`, signaling the end of the script. This will ingest and merge data directly into Neo4j.