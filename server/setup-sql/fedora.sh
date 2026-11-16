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
\l 
SQL

#Restart the computer here
echo "Setup complete. Restart your Linux server."
