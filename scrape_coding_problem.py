import read_gmail
import base64
import nbformat as nbf
import os

# TODO: Comment code
# TODO: Only create files if they don't exist already. Pull existing ones with os.listdir?

service = read_gmail.auth_gmail_api()

messages = read_gmail.list_messages(service, query='subject:"Daily Coding Problem: Problem #"')

for message in messages:
    content = read_gmail.get_message(service, message['id'])
    subject = content['payload']['headers'][16]['value']

    text = content['payload']['parts'][0]['body']['data']
    msg_str = base64.urlsafe_b64decode(text).decode()

    end = msg_str.find('Upgrade to premium')

    problem = msg_str[65:end].strip()

    nb = nbf.v4.new_notebook()

    nb['cells'] = [nbf.v4.new_markdown_cell('### ' + subject), nbf.v4.new_raw_cell(problem), nbf.v4.new_code_cell()]

    folder = 'Problems/'
    file_name = subject.replace('Problem: ', '').replace('#', '') + '.ipynb'
    file_path = folder + file_name

    if not os.path.exists(folder):
        os.mkdir(folder)

    try:
        if not os.path.exists(file_path):
            print('Creating', file_path)
            with open(file_path, 'w', encoding="utf-8") as f:
                nbf.write(nb, f)
        else:
            print('File already exists. Skipping')
    except (UnicodeEncodeError, TypeError) as error:
        print(error)
