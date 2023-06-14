SLACK_BOT_TOKEN = "xoxb-5423294921907-5420504884997-4pQzwlfJUQHoJsEe7grxwYW0"
SLACK_APP_TOKEN = "xapp-1-A05C0S7BH71-5425870179988-df1ac8225bd247a3aae5d2572c13b0dfbfff13069e9b90f9cb29ca733ae1f870"
OPENAI_API_KEY  = "8ef6f79ff84c42f0944d0961f2394cf2"

import os
import openai
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_bolt import App

# OpenAI Configuration
openai.api_type="azure"
openai.api_base = "https://ai-stg.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = OPENAI_API_KEY

# Event API & Web API
app = App(token=SLACK_BOT_TOKEN) 
client = WebClient(SLACK_BOT_TOKEN)

# This gets activated when the bot is tagged in a channel    
@app.event("app_mention")
def handle_message_events(body, logger):
    # Log message
    print(str(body["event"]["text"]).split(">")[1])
    
    # Create prompt for ChatGPT
    prompt = str(body["event"]["text"]).split(">")[1]
    
    # Let thre user know that we are busy with the request 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Hello from your bot! :robot_face: \nThanks for your request, I'm on it!")
    
    # Check ChatGPT
    response = openai.Completion.create(
        engine="elementor-gpt-35-turbu-0301",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,

        temperature=0.5).choices[0].text
    
    # Extract the reply from the API response
    
    # Reply to thread 
    client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Here you go: \n{response}")

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()