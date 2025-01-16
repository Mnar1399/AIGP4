import requests
import os

# Azure configuration
text_analytics_endpoint = os.getenv("TEXT_ANALYTICS_ENDPOINT", "https://projectgame.cognitiveservices.azure.com/")
text_analytics_key = os.getenv("TEXT_ANALYTICS_KEY", "2KzapW8uHvXU36izit7Gqf299IOmrOfeBnNFCPnI3uczFZsiQDVJJQQJ99AKACYeBjFXJ3w3AAAaACOGPojV")
openai_endpoint = os.getenv("OPENAI_ENDPOINT", "https://botgame.openai.azure.com")
openai_key = os.getenv("OPENAI_KEY", "EyoMKPi0cdmUAujXRhLdlPew6vrPnHr9Zyj0EswXpopsuerw3MQ7JQQJ99ALACYeBjFXJ3w3AAABACOGfOMX")

def send_post_request(url, headers, data):
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Connection error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

def analyze_key_phrases(text, endpoint, key):
    url = f"{endpoint}/text/analytics/v3.1/keyPhrases"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json",
    }
    data = {"documents": [{"id": "1", "language": "en", "text": text}]}
    return send_post_request(url, headers, data)



def analyze_game_idea(game_name, openai_endpoint, openai_key):
    
    url = f"{openai_endpoint}/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": openai_key,
    }
    data = {
        "messages": [
            {"role": "system", "content": "You are a creative game designer. Write a 5-sentence concept for a game based on the given name."},
            {"role": "user", "content": f"The game name is '{game_name}'. Please provide a creative idea for this game."},
        ],
        "max_tokens": 150,
        "temperature": 0.7,
    }
    game_name = "Maze Runner"  # مثال لاسم اللعبة الناتج من التحليل
    
    response = send_post_request(url, headers, data)
    return response
    


def analyze_project_cost(details):
    url = f"{openai_endpoint}/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview"
    headers = {"Content-Type": "application/json", "api-key": openai_key}
    data = {
        "messages": [
            {"role": "system", "content": "You are an expert in game development project budgeting."},
            {"role": "user", "content": details},
        ],
        "max_tokens": 200,
        "temperature": 0.7,
    }
    return send_post_request(url, headers, data)
