import os
import requests
from google import genai # New import

def run_task():
    # 1. Fetch the Quote
    resp = requests.get("https://zenquotes.io/api/random")
    quote_data = resp.json()[0]
    original_quote = quote_data['q']
    
    # 2. Use the New Gemini Client
    # The new SDK automatically looks for an env var named 'GOOGLE_API_KEY'
    # but we will pass it explicitly to be safe.
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = f"Here is a famous quote: '{original_quote}'. Give me a 1-sentence 'vibe check' or modern explanation of this quote for a developer."
    
    # New method call: client.models.generate_content
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    
    # 3. Format and Send to Discord
    message = (
        f"**Daily Inspiration:**\n> {original_quote}\n\n"
        f"**🤖 AI Vibe Check:** {response.text}"
    )

    webhook_url = os.environ.get("DISCORD_WEBHOOK")
    if webhook_url:
        requests.post(webhook_url, json={"content": message})
        print("✅ Success!")
    else:
        print(message)

if __name__ == "__main__":
    run_task()