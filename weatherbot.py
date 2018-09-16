import os
import time
import re
from slackclient import SlackClient
import requests
import json
from urllib.request import urlopen


# instantiate Slack client
# ID of slackbot is stored in file so as to avoid exposure of token to others while code is pushed to git
# Slackbot_ID fiel is added ti gitignore
text_file = open("Slackbot_ID","r")
SlackBot_ID = text_file.read()
slack_client = SlackClient(SlackBot_ID)
text_file.close()

# starterbot's user ID in Slack: value is assigned after the bot starts up
SlackBot_ID = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
HELP_COMMAND = "help"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(HELP_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(HELP_COMMAND):
        response = "Enter name of city to get weather information"
    else:
        """
        #api = "http://autocomplete.wunderground.com/aq?query=" + command
        api = "http://api.wunderground.com/api/http://api.wunderground.com/a Your_Key/conditions/q/CA/San_Francisco.json"
        req = requests.get(api)
        print(req.json())
        """

        text_file = open("openweather_ID", "r")
        APPPID = text_file.read()
        text_file.close()
        url = 'http://api.openweathermap.org/data/2.5/weather?q=' + command + '&APPID=' + APPPID

        try:

            f = urlopen(url)

            json_string = f.read()

            parsed_json = json.loads(json_string)
            print(parsed_json)
            response = parsed_json

            response = "Temperature : " + str(int(response["main"]["temp"]) - 273) + "C" + "\n" + "Pressure : " + str(
                response["main"]["pressure"]) + " atm" + "\n" + "Humidity : " + str(
                response["main"]["humidity"]) + "\n" + "Wind speed : " + str(
                response["wind"]["speed"]) + " mph" + "\n" + "Clouds : " + str(response["weather"][0]["description"])

        except:
            response = "Can not find weather information for requested city name"


    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
