import os
import requests
import json
import google.generativeai as genai

def run_task():
    # 1. Fetch the Quote
    resp = requests.get("https://zenquotes.io/api/random")
    quote_data = resp.json()[0]
    original_quote = quote_data['q']
    
    # 2. Use Gemini to "Explain" it
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"Here is a famous quote: '{original_quote}'. Give me a 1-sentence 'vibe check' or modern explanation of this quote for a developer."
    ai_response = model.generate_content(prompt)
    
    # 3. Format the Discord Message
    message = (
        f"**Daily Inspiration:**\n> {original_quote}\n\n"
        f"**🤖 AI Vibe Check:** {ai_response.text}"
    )

    # 4. Send to Discord
    webhook_url = os.environ.get("DISCORD_WEBHOOK")
    requests.post(webhook_url, json={"content": message})

if __name__ == "__main__":
    run_task()