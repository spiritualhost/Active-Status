#!/usr/bin/env bash
set -e

#Initial update
sudo dnf upgrade -y
sudo dnf autoremove -y
sudo dnf clean all

#Upgrade the database
sudo dnf install postgresql-upgrade meld
sudo postgresql-setup --upgrade

#Start postgresql
systemctl start postgresql

#Rebuild indexes as the postgres user
sudo -u postgres reindexdb --all

#Restore configuration
sudo meld /var/lib/pgsql/data{,-old}/postgresql.conf
sudo meld /var/lib/pgsql/data{,-old}/pg_hba.conf