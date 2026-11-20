#!/usr/bin/env bash
set -e

#Initial update
sudo dnf upgrade -y
sudo dnf autoremove -y
sudo dnf clean all

#Configure system to prevent automatic suspension and hibernation (in effect after reboot)
sudo mkdir -p /etc/systemd/sleep.conf.d/
sudo tee /etc/systemd/sleep.conf.d/nosuspend.conf >/dev/null <<'EOF'
[Sleep]
AllowSuspend=no
AllowHibernate=no
AllowHybridSleep=no
AllowSuspendThenHibernate=no
EOF

#Installation of necessary packages
sudo dnf install postgresql-server postgresql-contrib -y

#Set postgresql server to run at boot
sudo systemctl enable postgresql

#Initialize the database
sudo postgresql-setup --initdb --unit postgresql

#Start postgresql server
sudo systemctl start postgresql

#User creation and database creation
sudo -u postgres psql <<'SQL'

-- Set up default passwords for users
CREATE USER write_only WITH PASSWORD 'PasswordWrite1';
CREATE USER read_only WITH PASSWORD 'PasswordRead1';
CREATE USER as_admin WITH PASSWORD 'Admin1';

-- Create Active Status database
CREATE DATABASE active_status OWNER as_admin;

-- Switch into database, create servers table, and make additional changes
\c active_status
CREATE TABLE IF NOT EXISTS servers (
    date DATE,
    hostname TEXT,
    activation_period DOUBLE PRECISION
);

-- Allow both read_only and write_only to connect to the database and access the public schema
GRANT CONNECT ON DATABASE active_status TO read_only, write_only;
GRANT USAGE ON SCHEMA public TO read_only, write_only;

-- Grant read only access (SELECT)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO read_only;

-- Grant write only access (INSERT only -- cannot SELECT, UPDATE, or DELETE)
GRANT INSERT ON ALL TABLES IN SCHEMA public TO write_only;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT INSERT ON TABLES TO write_only;

-- View results
\d servers
SQL

#Reload postgresql
sudo systemctl reload postgresql

#Firewall setup
sudo firewall-cmd --permanent --add-port=5432/tcp 

sudo -u postgres psql -c "ALTER SYSTEM SET listen_addresses TO '*';" && sudo systemctl restart postgresql

HBA=$(sudo -u postgres psql -t -P format=unaligned -c 'SHOW hba_file;') && echo "host all all 0.0.0.0/0 scram-sha-256" | sudo tee -a "$HBA" && sudo systemctl reload postgresql

#Restart the computer here
echo "Setup complete. Restart your Linux server."
