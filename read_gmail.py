"""
This module is for reading the contents of Gmail messages
It contains three functions to authenticate with the Gmail API, get a list of messages that match a query,
and read the contents of the messages from the list.
"""

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def auth_gmail_api():
    """
    Authenticates with Gmail api to enable reading emails
    Copied directly from Google API quickstart tutorial, with minor modifications
    https://developers.google.com/gmail/api/quickstart/python
    :return:
    service object
    """

    # If modifying these scopes, delete the file token.pickle.
    scope = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('creds/token.pickle'):
        with open('creds/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds/credentials.json', scope)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('creds/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def list_messages(service, query=''):
    """
    Creates a list of emails that match the query
    :param service:
    service object created upon authentication
    :param query:
    string to query for
    :return messages:
    list of message objects
    """

    response = service.users().messages().list(userId='me', q=query).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId='me', q=query,
                                                   pageToken=page_token).execute()
        messages.extend(response['messages'])

    return messages


def get_message(service, msg_id):
    """
    Gets Gmail message content using the message ID
    :param service:
    service object created upon authentication
    :param msg_id:
    id of the Gmail message. Intended to be gained from list_messages function
    :return message:
    content of message as a dictionary
    """
    message = service.users().messages().get(userId='me', id=msg_id).execute()

    return message
