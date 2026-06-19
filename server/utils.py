#Utils for assisting the server daemon
import psycopg2, configparser, os
from datetime import datetime
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

    def scan_query(self, conn: psycopg2.extensions.connection):
        return        

#Email setup
class EMAIL_SETUP:
    def __init__(self):
        return