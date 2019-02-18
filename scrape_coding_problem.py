"""
The purpose of this script is to programmatically generate a Jupyter notebook file that contains the daily interview
question from Daily Coding Problem. Since these problems are sent daily via email, this script scrapes a Gmail account
for all daily coding problems, and tries to create the notebook file if it doesn't already exist. Currently, every time
the script runs, it will try to generate every question that is in the mail box. May change this to ignore the
questions that have already been generated.
"""

import read_gmail  # Small module built using the Gmail API to read emails
import base64
import nbformat as nbf
import os

# TODO: Only create files if they don't exist already. Pull existing ones with os.listdir?
# Authenticate with Gmail API and return service object. Uses credentials stored in /creds/credentials.json
# Will require a login on the first try, and then pickle the token for later use
service = read_gmail.auth_gmail_api()

# Pulls a list of message ids that match the query. In this case, the subjects will always contain the same text
messages = read_gmail.list_messages(service, query='subject:"Daily Coding Problem: Problem #"')

# Loop over the list of message ids, and use the Gmail API's get() function to acquire the message's content
for message in messages:
    content = read_gmail.get_message(service, message['id'])

    # Pulling the subject line from the email
    subject = content['payload']['headers'][16]['value']

    # Pulling the main body of text from the email and decoding it from base64
    text = content['payload']['parts'][0]['body']['data']
    msg_str = base64.urlsafe_b64decode(text).decode()

    # Trimming down the body text to just the question
    end = msg_str.find('Upgrade to premium')
    problem = msg_str[65:end].strip()

    # Creating a new Jupyter notebook object, and adding a cell for title, question, and solution
    nb = nbf.v4.new_notebook()
    nb['cells'] = [nbf.v4.new_markdown_cell('### ' + subject), nbf.v4.new_raw_cell(problem), nbf.v4.new_code_cell()]

    # Create file paths from the subject line. Everything will be place in ./Problems
    folder = 'Problems/'
    file_name = subject.replace('Problem: ', '').replace('#', '') + '.ipynb'
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
            print('File already exists. Skipping')
    except (UnicodeEncodeError, TypeError) as error:
        print(error)
