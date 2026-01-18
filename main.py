import requests

def run_task():
    print("🚀 Automation Started!")
    
    # Fetch a random quote from a free API
    response = requests.get("https://zenquotes.io/api/random")
    if response.status_code == 200:
        data = response.json()
        quote = data[0]['q']
        author = data[0]['a']
        print(f"Today's Inspiration: \"{quote}\" - {author}")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    run_task()