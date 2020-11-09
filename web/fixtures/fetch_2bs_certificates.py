#!/usr/bin/env python
# coding: utf-8

import argparse
import requests
import urllib.request
from bs4 import BeautifulSoup

import json
import pandas as pd
from datetime import date

from os import listdir
from os.path import isfile
import shutil
import re

validUrl = 'https://www.2bsvs.org/certificats-valides.html'
invalidUrl = 'https://www.2bsvs.org/certificats-retires.html'
DESTINATION_FOLDER = '/tmp/'



def download_certificates(url, valid=True):
    html_content = requests.get(url).text.replace('<br/>', ' ').replace('<br />', ' ')
    soup = BeautifulSoup(html_content, "lxml")
    table = soup.find_all('table')
    df = pd.read_html(str(table))[0]
    df = df[~df['Numéro 2BS'].isnull()] # Pour une raison inconnue, la ligne de coordonnées est dupliquée
    if valid:
        pd.DataFrame.to_csv(df, '%s/Certificates2BS_%s.csv' % (DESTINATION_FOLDER, str(date.today())), index=False)
    else:
        pd.DataFrame.to_csv(df, '%s/Certificates2BS_invalid_%s.csv' % (DESTINATION_FOLDER, str(date.today())), index=False)

def main():
    download_certificates(validUrl)
    download_certificates(invalidUrl, valid=False)
    
if __name__ == '__main__':
    main()
