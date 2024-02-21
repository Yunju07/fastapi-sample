from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def make_event(summary, location, date, attendee):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print(os.getcwd())
            flow = InstalledAppFlow.from_client_secrets_file(
                'calender_module/credential.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        event = {
            'summary': summary,
            'location': location,
            'description': summary,
            'start': {
                # 'dateTime': '2024-02-10T00:00:00+09:00',
                'dateTime': date,
                # 'timeZone': 'Asia/Seoul',
            },
            'end': {
                # 'dateTime': '2024-02-10T24:00:00+09:00',
                'dateTime': date,
                # 'timeZone': 'Asia/Seoul',
            },
            'recurrence': [
                # 'RRULE:FREQ=DAILY;COUNT=2'
            ],
            'attendees': [
                #{'email': attendee},
                # {'email': 'sbrin@example.com'},
            ],
            'reminders': {
                'useDefault': False,
                # 'overrides': [
                # {'method': 'email', 'minutes': 24 * 60},
                # {'method': 'popup', 'minutes': 10},
                # ],
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    except HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    print(os.getcwd())