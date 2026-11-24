#Script to automate the entire installation of the email server component of Active Status

#!/usr/bin/env bash
set -e

#Initial update
sudo dnf upgrade -y
sudo dnf autoremove -y
sudo dnf clean all

#Install dependencies idempotently
sudo dnf install libpq-devel python3-devel gcc 

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
OUTPUT="./dist/${APP_NAMER}"
if [[ -f "$OUTPUT" && -s "$OUTPUT" && -x "$OUTPUT" ]]; then
    echo "Successful: binary created at $OUTPUT"
else
    echo "Invalid binary." >&2
    exit 1
fi

#Clean up build files
sudo rm -rf build/

#Exit message
echo "Active Status is now set up."
read -r -p "Press Enter to continue..."
