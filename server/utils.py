#Utils for assisting the server daemon
import psycopg2, os
from datetime import datetime, date
from dotenv import load_dotenv

#SQL
class SQL_SCAN:
    def __init__(self):
        #Load variables from the .env file
        load_dotenv()

        self.database = os.getenv("DATABASE")
        self.user = os.getenv("USER")
        self.password = os.getenv("PASSWORD")
        self.host = os.getenv("HOST")
        self.port = os.getenv("PORT")

        return
    
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
            print(f'{datetime.now()}: Unable to make connection to SQL server. Is the firewall open for incoming traffic over the port specified in .env?: {e}')
            return False

    def scan_query(self, conn: psycopg2.extensions.connection, days_left: int):
        try:
            with conn.cursor() as cur:
                #Get today's date
                today = date.today()

                #Execute a query
                query = """
                    SELECT * 
                    FROM servers 
                    WHERE (activation_period::float / 1440) < %s
                        AND date = %s;
                """

                cur.execute(query, (days_left, today))

                #Fetch all the rows
                rows = cur.fetchall()

                #Iteratre through rows ***FIX THIS***
                applicable_machines = {}
                for row in rows:
                    hostname = row[1]
                    days_left = int(row[2] / 1440.0)
                    applicable_machines[hostname] = days_left

            return applicable_machines

        except Exception as e:
            print(f"General exception: {e}")
            return 1    

#Email setup
class EMAIL_SETUP:
    def __init__(self):
        return