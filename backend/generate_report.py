import sqlite3
import pandas as pd
import json
import os
from datetime import datetime

# DB Path
DB_PATH = "jobplatform.db"

def generate_csv():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # 1. Get all Search Queries
    query = """
    SELECT 
        sq.query_hash,
        sq.last_fetched,
        sq.params
    FROM search_queries sq
    ORDER BY sq.last_fetched DESC
    """
    
    try:
        df_queries = pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Error reading queries: {e}")
        return

    if df_queries.empty:
        print("⚠️ No search history found (Cache might be empty).")
        # Create empty CSV with headers
        pd.DataFrame(columns=[
            "Date", "Time", "Query", "Location", "Filters", "Total Results", "Source Breakdown"
        ]).to_csv("search_history_tracker.csv", index=False)
        return

    report_data = []

    for _, row in df_queries.iterrows():
        q_hash = row['query_hash']
        timestamp = row['last_fetched']
        
        # Parse params
        try:
            params = json.loads(row['params'])
        except:
            params = {}
            
        search_query = params.get('q') or params.get('query', 'N/A')
        locations = params.get('locations', [])
        if isinstance(locations, list):
            location_str = ", ".join(locations)
        else:
            location_str = str(locations)
            
        # Parse filters
        filters = []
        if params.get('experience'): filters.append(f"Exp: {params['experience']}")
        if params.get('ctc'): filters.append(f"CTC: {params['ctc']}")
        if params.get('country') and params.get('country') != 'India': filters.append(f"Country: {params['country']}")
        
        filter_str = "; ".join(filters) if filters else "None"
        
        # Get Job Stats for this query
        job_query = f"""
        SELECT source, COUNT(*) as count 
        FROM jobs 
        WHERE query_hash = '{q_hash}' 
        GROUP BY source
        """
        df_jobs = pd.read_sql_query(job_query, conn)
        
        total_results = df_jobs['count'].sum()
        
        # Format breakdown: "Adzuna: 10, LinkedIn: 2"
        breakdown_parts = []
        for _, job_row in df_jobs.iterrows():
            breakdown_parts.append(f"{job_row['source']}: {job_row['count']}")
        
        breakdown_str = " | ".join(breakdown_parts)
        
        # Split Timestamp
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        except:
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except:
                dt = datetime.now()

        report_data.append({
            "Date": dt.strftime("%Y-%m-%d"),
            "Time": dt.strftime("%H:%M:%S"),
            "Query": search_query,
            "Location": location_str,
            "Filters": filter_str,
            "Total Results": total_results,
            "Source Breakdown": breakdown_str
        })

    # Create DataFrame and Save
    df_report = pd.DataFrame(report_data)
    output_file = "search_history_tracker.csv"
    df_report.to_csv(output_file, index=False)
    
    print(f"✅ Report generated: {output_file}")
    print(df_report.head())

if __name__ == "__main__":
    generate_csv()
