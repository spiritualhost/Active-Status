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
CREATE USER write_only WITH PASSWORD 'PasswordWrite1';
CREATE USER read_only WITH PASSWORD 'PasswordRead1';
CREATE USER as_admin WITH PASSWORD 'Admin1';
CREATE DATABASE active_status OWNER as_admin;
GRANT pg_read_all_data TO read_only;
GRANT pg_write_all_data TO writeonly_user; 
\l 
SQL

#Reload postgresql
sudo systemctl reload postgresql

#Firewall setup
sudo firewall-cmd --permanent --add-port=5432/tcp 

sudo -u postgres psql -c "ALTER SYSTEM SET listen_addresses TO '*';" && sudo systemctl restart postgresql

HBA=$(sudo -u postgres psql -t -P format=unaligned -c 'SHOW hba_file;') && echo "host all all 0.0.0.0/0 scram-sha-256" | sudo tee -a "$HBA" && sudo systemctl reload postgresql

#Restart the computer here
echo "Setup complete. Restart your Linux server."
