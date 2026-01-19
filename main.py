import os
import requests
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

# 1. Smart Retry Logic for the Brain (Gemini 3)
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_ai_vibe(client, quote):
    # Prompt engineering: added constraints to keep response concise
    prompt = f"Give some examples from history (max 3 sentences) regarding this in Malayalam {quote}'"
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=prompt
    )
    return response.text

def run_task():
    # 2. Check Memory (History)
    history_file = "history.txt"
    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            f.write("--- Quote History ---\n")
    
    with open(history_file, "r") as f:
        past_quotes = f.read().splitlines()

    # 3. Fetch a Unique Quote (ZenQuotes)
    new_quote = ""
    author = ""
    for _ in range(5):  # Try 5 times to find a new one
        resp = requests.get("https://zenquotes.io/api/random")
        data = resp.json()[0]
        if data['q'] not in past_quotes:
            new_quote = data['q']
            author = data['a']
            break
    
    if not new_quote:
        print("Could not find a unique quote after 5 tries. Ending.")
        return

    # 4. Process with Gemini 3
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    try:
        vibe = get_ai_vibe(client, new_quote)
        
        # 5. Safety Truncation for Discord (2000 char limit)
        if len(vibe) > 1800:
            vibe = vibe[:1800] + "... [Truncated]"

        # 6. Save to History
        with open(history_file, "a") as f:
            f.write(new_quote + "\n")

        # 7. Prepare and Send to Discord
        payload = {
            "content": f"**Daily Inspiration:**\n> {new_quote}\n— *{author}*\n\n**🤖 AI Vibe Check:** {vibe}",
            "username": "Gemini 3 Bot"
        }
        
        webhook_url = os.environ.get("DISCORD_WEBHOOK")
        if webhook_url:
            result = requests.post(webhook_url, json=payload)
            print(f"Discord Response Code: {result.status_code}")
            if result.status_code == 204:
                print("✅ Successfully sent to Discord and updated history.")
            else:
                print(f"⚠️ Discord Error: {result.text}")
                
    except Exception as e:
        print(f"❌ Automation failed: {e}")

if __name__ == "__main__":
    run_task()