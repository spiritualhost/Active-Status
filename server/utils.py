#Utils for assisting the server daemon
import psycopg2, os, smtplib, ssl
from email.message import EmailMessage
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
class EMAIL_NOTIFICATION:
    def __init__(self, email: str, applicable_machines: dict, smtp_server: str, port: int, sender_email: str, sender_password: str):
        self.email = email
        self.table = applicable_machines
        self.server = smtp_server
        self.port = port
        self.sender_email = sender_email
        self.sender_password = sender_password
        return

    def email_setup(self):
        print(f"Setting up email notification to address: {self.email}")

        #Get today's date
        today = date.today()

        #Configuration details here
        #Need to figure this out, preferably not plaintext

        #Build the email message
        msg = EmailMessage()
        msg["Subject"] = f"Machine Status - {today}"
        msg["From"] = self.sender_email
        msg["To"] = self.email

        html = """\
            <!DOCTYPE html>
            <html>
                <body style="background-color: #f0f4f8;">
                    <p><i>The following machines fall below the threshold you set:</i></p>
        """

        print(self.table)

        #Set up pretty table for email message
        html += '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f2f2f2;">'
        html += '<th style="border-bottom: 2px solid #333; padding: 8px; text-align: left;">' + 'machine' + '</th>'
        html += '<th style="border-bottom: 2px solid #333; padding: 8px; text-align: left;">' + 'days left' + '</th>'
        html += '</tr>'
   
        for machine, days in self.table.items():
            html += '<tr style="background-color: #f2f2f2;">'
            html += '<td style="border-bottom: 1px solid #ddd; padding: 8px;">' + machine + '</td>'
            html += '<td style="border-bottom: 1px solid #ddd; padding: 8px;">' + str(days) + ' days left.</td>'
            html += '</tr>'
        html += '</table>'

        html += """\
                </body>
            </html>
        """

        msg.add_alternative(html, subtype="html")

        return msg

    #Establish a secure connection to the smtp server and send
    def send_email(self, msg):
        try:
            #Create a standard security context configuration
            context = ssl.create_default_context()

            #Establish a TLS connection to the server
            with smtplib.SMTP(self.server, self.port) as server:
                #Send EHLO to SMTP server to identify self
                server.ehlo()

                server.starttls(context=context)

                server.ehlo()

                #Authenticate and transmit the payload
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

                print("Secure email transmission!")    
            
                return 0
        
        except Exception as e:
            print(f"An error occurred: {e}")