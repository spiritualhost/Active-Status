#Script to automate the entire installation of the email server component of Active Status

#!/usr/bin/env bash
set -e

#Initial update
sudo dnf upgrade -y
sudo dnf autoremove -y
sudo dnf clean all

#Install dependencies idempotently
sudo dnf install libpq-devel python3-devel gcc -y

#Set up and enter virtual environment
python3 -m venv .venv
source .venv/bin/activate

#Install dependencies
pip install -r requirements.txt

#Compile with pyinstaller
pyinstaller active-status-daemon.spec

#Deactivate virtual environment
deactivate

#Confirm output exists (-f), is not empty (-s), and is executable (-x)
APP_NAME="active-status-daemon"
OUTPUT="./dist/${APP_NAME}"
if [[ -f "$OUTPUT" && -s "$OUTPUT" && -x "$OUTPUT" ]]; then
    echo "Successful: binary created at $OUTPUT"
    sudo chmod +x "$OUTPUT"
else
    echo "Invalid binary." >&2
    exit 1
fi

#Clean up build files
sudo rm -rf build/

#Set up cronjob
DIST_PATH="$PWD/dist/"
USERNAME="$USER"
CRON_JOB="0 17 * * * cd '$DIST_PATH' && ./active-status-daemon --db_check  >> /home/$USERNAME/active-status-cron.log 2>&1"
(crontab -l 2>/dev/null || true; echo "$CRON_JOB") | crontab -
crontab -l

#Exit message
echo "Active Status is now set up."
read -r -p "Press Enter to continue..."
