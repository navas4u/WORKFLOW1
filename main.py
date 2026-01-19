import requests
import os
import json

def run_task():
    # 1. Fetch the data
    response = requests.get("https://zenquotes.io/api/random")
    if response.status_code == 200:
        data = response.json()
        quote = data[0]['q']
        author = data[0]['a']
        message = f"**Inspiration for Today:**\n> {quote}\n— *{author}*"
        
        # 2. Send to Discord
        webhook_url = os.environ.get("DISCORD_WEBHOOK")
        
        if webhook_url:
            payload = {"content": message}
            headers = {"Content-Type": "application/json"}
            requests.post(webhook_url, data=json.dumps(payload), headers=headers)
            print("✅ Message sent to Discord!")
        else:
            print("❌ No Discord Webhook found. Printing to console instead:")
            print(message)
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    run_task()
