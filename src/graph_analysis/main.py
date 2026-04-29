import spacy
from google.cloud import bigquery
from neo4j import GraphDatabase
from dotenv import load_dotenv
from graph_analysis.util import *
from graph_analysis.config import *

# BigQuery
bq_client = bigquery.Client()

# Query Top 10 Businesses
query_job = bq_client.query("""
WITH topten AS (
    SELECT
    DISTINCT
        business_id,
        business_review_count
    FROM `project-9b9e551b-e2f7-46a3-b22.intermediate.int_business_categories`
    WHERE country = 'United States'
        AND state = 'CA'
        AND is_open IS TRUE
        AND category IN ('Restaurants', 'Food')
    ORDER BY business_review_count DESC
    LIMIT 10
), base AS (
    SELECT
        reviews.review_id,
        reviews.user_id,
        reviews.business_id,
        reviews.business_name,
        reviews.review_text,
        ARRAY_SLICE(SPLIT(friends_raw, ','), 0, 10) AS friends
    FROM topten
    INNER JOIN `project-9b9e551b-e2f7-46a3-b22.intermediate.int_business_reviews` reviews
        ON topten.business_id = reviews.business_id
    INNER JOIN `project-9b9e551b-e2f7-46a3-b22.staging.stg_users` users
        ON reviews.user_id = users.user_id
)

SELECT *
FROM base
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY business_id
    ORDER BY review_id
) <= 10

""")

query_job2 = bq_client.query("""
WITH topten AS (
    SELECT
    DISTINCT
        business_id,
        business_review_count
    FROM `project-9b9e551b-e2f7-46a3-b22.intermediate.int_business_categories`
    WHERE country = 'United States'
        AND state = 'CA'
        AND is_open IS TRUE
        AND category IN ('Restaurants', 'Food')
    ORDER BY business_review_count DESC
    LIMIT 10
), base AS (
    SELECT
        reviews.review_id,
        reviews.user_id,
        reviews.business_id,
        reviews.business_name,
        reviews.review_text,
        ARRAY_SLICE(SPLIT(friends_raw, ','), 0, 10) AS friends
    FROM topten
    INNER JOIN `project-9b9e551b-e2f7-46a3-b22.intermediate.int_business_reviews` reviews
        ON topten.business_id = reviews.business_id
    INNER JOIN `project-9b9e551b-e2f7-46a3-b22.staging.stg_users` users
        ON reviews.user_id = users.user_id
)

SELECT id, reviews.business_id, reviews.business_name FROM (SELECT *
FROM base
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY business_id
    ORDER BY review_id
) <= 10) a,
UNNEST(a.friends) AS id
INNER JOIN `project-9b9e551b-e2f7-46a3-b22.intermediate.int_business_reviews` reviews
    ON id = reviews.user_id
""")

# Basic Logging
print(f"""
Querying {bq_client.project}:
Cache hit:
\tQuery 1: {query_job.cache_hit}
\tQuery 2: {query_job2.cache_hit}
Job ID:
\tQuery 1: {query_job.job_id}
\tQuery 2: {query_job2.job_id}
State:
\tQuery 1: {query_job.state}
\tQuery 2: {query_job2.state}
Total bytes processed:
\tQuery 1: {query_job.total_bytes_processed}
\tQuery 2: {query_job2.total_bytes_processed}
""")

# Initialize NLP
nlp = spacy.load('en_core_web_sm')

# Neo4j Ingestion
print(f'Ingesting data into Neo4j...')
with GraphDatabase.driver(uri=NEO_URI, auth=NEO_AUTH) as driver:
    with driver.session() as session:
        for row in query_job.result():
            review_summary = extract_aspect_sentiment(row.review_text, nlp)

            session.run("""
            MERGE (u:User {id: $user_id})
            MERGE (b:Business {id: $business_id})
            SET b.name = $business_name
            SET b.toptier = true
            MERGE (u)-[v:VISITED]-(b)
            UNWIND $review_summary AS review
            MERGE (r:Review {summary: review})
            MERGE (u)-[:WROTE]->(r)  
            MERGE (b)-[rel:HAS_PHRASE]->(r)
                ON CREATE SET rel.weight = 1
                ON MATCH SET rel.weight = rel.weight + 1
            WITH u
        
            UNWIND $friends AS friend_id
            MERGE (f:User {id: friend_id})
            MERGE (u)-[rel:FRIENDSWITH]-(f)
            """, user_id=row.user_id, business_id=row.business_id, business_name=row.business_name, review_summary=review_summary, friends=row.friends)
        for row in query_job2.result():
            session.run("""
            MERGE (u:User {id: $user_id})
            MERGE (b:Business {id: $business_id, name: $business_name})
            MERGE (u)-[v:VISITED]-(b)
            """, user_id=row.id, business_id=row.business_id, business_name=row.business_name)
print('Done!')