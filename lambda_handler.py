'''
Feedbackbot - sns2slack
Subscribing To SNS For Slack Notifications
Part of https://woobot.io/weve-got-somethin-for-ya/
'''

import os
import logging
import json
# We use urllib2 instead of requests just to make the demo easier
# In a production environment, consider using the requests library
from urllib2 import Request, urlopen, URLError, HTTPError

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

FEEDBACK_CHANNEL = os.environ.get('feedback_channel')
FEEDBACK_SLACK_NAME = os.environ.get('feedback_slack_name')
FEEDBACK_SLACK_EMOJI = os.environ.get('feedback_slack_emoji')
FEEDBACK_SLACK_URL = os.environ.get('feedback_slack_url')

def lambda_handler(event, context):
    ''' Receive SNS and send to Slack '''

    for record in event['Records']:
        if 'Sns' not in record:
            LOGGER.warn('ERROR ABANDON RECORD:  Not an SNS event')
            continue

        subject = record['Sns']['Subject']

        if subject != 'feedback':
            LOGGER.warn('Non-feedback message in feedback SNS')
            continue

        feedback = json.loads(record['Sns']['Message'])

        msgtext = '`%s` (%s) from `%s` (%s) says: ```%s```' % (feedback['user_name'], feedback['user_id'], feedback['team_domain'], feedback['team_id'], feedback['text'])

        slack_message = {
            'text' : msgtext,
            'mrkdwn': True,
            'channel': FEEDBACK_CHANNEL,
            'username': FEEDBACK_SLACK_NAME,
            'icon_emoji': FEEDBACK_SLACK_EMOJI
        }
        slack_url = FEEDBACK_SLACK_URL
        req = Request(slack_url, json.dumps(slack_message))
        try:
            response = urlopen(req)
            response.read()
            LOGGER.info('Message posted')
        except HTTPError as exc:
            LOGGER.error('Request failed: %d %s', exc.code, exc.reason)
        except URLError as exc:
            LOGGER.error('Server connection failed: %s', exc.reason)
