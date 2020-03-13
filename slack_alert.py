import os
import slack
import asyncio

bot_oauth_token = os.environ['SLACK_API_TOKEN']
sc = slack.WebClient(token=bot_oauth_token, run_async=True)
loop = asyncio.get_event_loop()

def post(channel, message):
    res = loop.run_until_complete(sc.chat_postMessage(channel=channel, text=message))
    if res['ok'] == False:
        print(res['error'])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Send a message to a slack channel')
    parser.add_argument('channel', help='Destination channel')
    parser.add_argument('message', nargs='+', help='Message to send')
    args = parser.parse_args()
    post(args.channel, ' '.join(args.message))
