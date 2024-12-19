import psycopg2
import requests
from datetime import datetime, timedelta

# Supabase connection details
DATABASE_URL = "postgresql://postgres:DLRntf503*!]MCmd67\:@db.blofihdgffvtiagexpys.supabase.co:5432/postgres"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "DLRntf503*!]MCmd67\:"
DATABASE_NAME = "statuses"

# HTTP request URL for alerts
ALERT_URL = "https://your-alert-endpoint.com"

# Thresholds
LOW_THRESHOLD = 10  # Failures to move from green to yellow
HIGH_THRESHOLD = 20  # Failures to move from yellow to red

def fetch_test_data():
    """
    Fetch test outcomes from the SQL table for the last 30 minutes.
    """
    query = """
        SELECT phone_number, sip_response, result, date_time
        FROM test_outcomes
        WHERE date_time >= %s;
    """
    try:
        conn = psycopg2.connect(
            dbname=DATABASE_NAME, user=DATABASE_USER,
            password=DATABASE_PASSWORD, host=DATABASE_URL
        )
        cursor = conn.cursor()
        thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
        cursor.execute(query, (thirty_minutes_ago,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print("Error fetching test outcomes:", e)
        return []

def calculate_status(failures):
    """
    Calculate the status based on failure count.
    """
    if failures > HIGH_THRESHOLD:
        return "red"
    elif failures > LOW_THRESHOLD:
        return "yellow"
    else:
        return "green"

def send_alert(failures, status):
    """
    Send an alert via HTTP POST request.
    """
    payload = {
        "message": f"Test calls threshold crossed. Failures: {failures}, Status: {status}",
        "timestamp": datetime.now().isoformat()
    }
    try:
        response = requests.post(ALERT_URL, json=payload)
        if response.status_code == 200:
            print("Alert sent successfully!")
        else:
            print("Failed to send alert:", response.status_code, response.text)
    except Exception as e:
        print("Error sending alert:", e)

def update_status_table(status):
    """
    Update the statuses table in the database with the new status.
    """
    update_query = """
        UPDATE statuses
        SET status = %s, last_updated = %s
        WHERE country = 'Global';  -- Adjust based on your table schema
    """
    try:
        conn = psycopg2.connect(
            dbname=DATABASE_NAME, user=DATABASE_USER,
            password=DATABASE_PASSWORD, host=DATABASE_URL
        )
        cursor = conn.cursor()
        cursor.execute(update_query, (status, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
        print("Statuses table updated successfully!")
    except Exception as e:
        print("Error updating statuses table:", e)

def main():
    # Fetch test outcomes
    test_data = fetch_test_data()

    # Calculate the number of failures
    failures = sum(1 for row in test_data if row[2].lower() == "failure")
    print(f"Failures in last 30 minutes: {failures}")

    # Determine the status
    status = calculate_status(failures)

    # Send alert if necessary
    if status != "green":
        send_alert(failures, status)

    # Update the statuses table
    update_status_table(status)

if __name__ == "__main__":
    main()
