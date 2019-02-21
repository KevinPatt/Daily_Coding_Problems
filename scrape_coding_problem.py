"""
The purpose of this script is to programmatically generate Jupyter notebook files that contain daily interview
questions from Daily Coding Problem. Since these problems are sent daily via email, this script scrapes a Gmail account
for all daily coding problems, determines what problems still need to be generated, then generates a Jupyter notebook
file for every missing problem in the ./Problems folder.

Required Packages:
read_gmail module (local)
base64
nbformat
"""

import read_gmail  # Small module built using the Gmail API to read emails
import base64
import nbformat as nbf
import os
from glob import glob

# Authenticate with Gmail API and return service object. Uses credentials stored in /creds/credentials.json
# Will require a login on the first try, and then pickle the token for later use
service = read_gmail.auth_gmail_api()

# Pulls a list of message ids that match the query. In this case, the subjects will always contain the same text
messages = read_gmail.list_messages(service, query='subject:"Daily Coding Problem: Problem #"')

# Find latest problem number and already generated notebooks
latest_q = len(messages)
notebooks = glob('./Problems/*.ipynb')
latest_n = notebooks[-1].split('\\')
latest_n = int(latest_n[-1][:3])

# Discover missing daily problems
nb_to_scrape = []
for i in range(1, latest_q+1):
    check_file = '{0:03d}'.format(i)
    if check_file not in str(notebooks):
        nb_to_scrape.append(check_file)

print('Scraping problems', ', '.join(nb_to_scrape))

# Loop over the list of problem numbers to scrape
for i in nb_to_scrape:
    message_index = latest_q - int(i)
    content = read_gmail.get_message(service, messages[message_index]['id'])

    # Pulling the subject line from the email
    subject = content['payload']['headers'][16]['value']
    # Grab problem number from the subject line after the # sign and pad with zeros
    problem_num = subject[subject.find('#')+1:].zfill(3)

    # Pulling the main body of text from the email and decoding it from base64
    text = content['payload']['parts'][0]['body']['data']
    msg_str = base64.urlsafe_b64decode(text).decode()

    # Trimming down the body text to just the question.
    end = msg_str.find('Upgrade to premium')
    problem = msg_str[65:end].strip()

    # Creating a new Jupyter notebook object, and adding a cell for title, question, and solution
    nb = nbf.v4.new_notebook()
    nb['cells'] = [nbf.v4.new_markdown_cell('### ' + subject), nbf.v4.new_raw_cell(problem), nbf.v4.new_code_cell()]

    # Create file paths from the subject line. Everything will be place in ./Problems
    folder = 'Problems/'
    file_name = problem_num + '.ipynb'
    file_path = folder + file_name

    # Making sure that the problem storage folder exists, otherwise this script will fail
    if not os.path.exists(folder):
        os.mkdir(folder)

    # Write the notebook object out a file if it doesn't already exist
    try:
        if not os.path.exists(file_path):
            print('Creating', file_path)
            with open(file_path, 'w', encoding="utf-8") as f:
                nbf.write(nb, f)
        else:
            print(file_name, 'already exists. Skipping')
    except (UnicodeEncodeError, TypeError) as error:
        print(error)
