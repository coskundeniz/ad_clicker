#!/bin/bash

project_dir=$(pwd)

# get password for Tor setup
tor_pwd=""
echo "Enter a password for tor network setup"
read tor_pwd

echo "Setting environment variable TOR_PWD..."
echo "export TOR_PWD=$tor_pwd" >> ~/.bashrc
source ~/.bashrc
cd $project_dir

echo "Installing Tor package..."
sudo apt update
sudo apt install -y tor

echo "Installing privoxy package..."
sudo apt install -y privoxy

# create virtual environment and activate
echo "Creating virtual environment..."
python -m venv env
source env/bin/activate

# install requirements
echo "Installing required packages..."
pip install wheel
pip install -r requirements.txt

# run as root
sudo su - <<EOF
echo "Making changes as root..."

port_enabled=$(egrep "^ControlPort 9051" /etc/tor/torrc)
if [[ -z "${port_enabled}" ]]; then
    echo "Enabling control port..."
    echo "ControlPort 9051" >> /etc/tor/torrc
fi

echo "Setting hashed Tor password..."
echo HashedControlPassword $(tor --hash-password "${tor_pwd}" | tail -n 1) >> /etc/tor/torrc

echo "Starting Tor service..."
service tor restart

echo "Setting privoxy config..."
echo "forward-socks5t / 127.0.0.1:9050 ." >> /etc/privoxy/config
service privoxy start
EOF

echo "::::: Setup Completed :::::"

# add run command as help
echo -e "\nRun the following commands to start"
echo "source env/bin/activate"
echo "python ad_clicker.py -q <search keywords>"
