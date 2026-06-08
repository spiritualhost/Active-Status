import subprocess, math, sqlite3, socket, sys
from datetime import date

def heartbeat(period_remaining: float):
    #Try to get hostname
    try:
        hostname = socket.gethostname()
    except Exception as e:
        print("Hostname not found: {e}")
        sys._exit(1)

    #Get date
    today = date.today()

    #Connect to a sqlite database
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()

    #Create table if it doesn't exist already
    cursor.execute("CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY, date DATE, hostname TEXT, activation_period INTEGER)")

    #Insert a single record
    cursor.execute("INSERT INTO servers (date, hostname, activation_period) VALUES (?, ?, ?)", (f"{today}", f"{hostname}", f"{period_remaining}"))

    #Save changes and close connection
    conn.commit()
    conn.close()
    
    return 0

commands = """
$product = (Get-WmiObject -Query "SELECT * FROM SoftwareLicensingProduct WHERE PartialProductKey IS NOT NULL")
$product.GracePeriodRemaining
"""

if __name__ == "__main__":
    print("Test")
    result = subprocess.run(
        ["powershell", "-Command", commands],
        capture_output=True,
        text=True)
    
    raw_period = result.stdout

    period_remaining = float(raw_period) if raw_period != "0\n0\n" else math.inf  

    print(type(period_remaining))
    print(period_remaining)

    #Heartbeat to SQL server
    heartbeat(period_remaining)