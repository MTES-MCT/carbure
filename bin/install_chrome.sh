#!/bin/bash

# Installer Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get -f install -y

# Installer ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
rm /tmp/chromedriver.zip google-chrome-stable_current_amd64.deb