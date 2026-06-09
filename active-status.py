import subprocess, math, psycopg2, socket, os
from datetime import date
from dotenv import load_dotenv
    
class PGSQL_CONNECTION:
    
    def __init__(self):
        #Load variables from the .env file
        load_dotenv()

        self.database = os.getenv("DATABASE")
        self.user = os.getenv("USER")        
        self.password = os.getenv("PASSWORD")        
        self.host = os.getenv("HOST")        
        self.port = os.getenv("PORT")        
    
    def confirm_connection(self):
        try:
            return psycopg2.connect(
                dbname=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
        except Exception as e:
            #print(f"Exception: {e}")
            return False

def heartbeat(conn: psycopg2.extensions.connection, period_remaining: float):
    try:
        #Set up connection to SQL database
        cur = conn.cursor()

        #Try to get hostname
        try:
            hostname = socket.gethostname()
        except Exception as e:
            print("Hostname not found: {e}")
            return 1

        #Get date
        today = date.today()

        #Insert a single record
        cur.execute("INSERT INTO servers (date, hostname, activation_period) VALUES (%s, %s, %s);", (today, hostname, period_remaining))

        #Save changes and close connection
        conn.commit()
        cur.close()
        conn.close()
        
        return 0
    
    except Exception as e:
        #print(f"Exception: {e}")
        return 1


commands = """
$product = (Get-WmiObject -Query "SELECT * FROM SoftwareLicensingProduct WHERE PartialProductKey IS NOT NULL")
$product.GracePeriodRemaining
"""

if __name__ == "__main__":

    #Instatiation of server connection object
    serv_connect = PGSQL_CONNECTION()
    conn = serv_connect.confirm_connection()

    #Query for activation info
    result = subprocess.run(
        ["powershell", "-Command", commands],
        capture_output=True,
        text=True)
    raw_period = result.stdout
    period_remaining = float(raw_period) if raw_period != "0\n0\n" else math.inf  

    #Heartbeat to SQL server
    heartbeat(conn, period_remaining)