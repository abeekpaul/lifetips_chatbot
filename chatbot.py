import requests
import bot_config

class ChatbotAssistant:
    def __init__(self):
        self.telegram_token = bot_config.TG_ACCESS_TOKEN
        self.endpoint_url = f"{bot_config.GPT_BASICURL}/deployments/{bot_config.GPT_MODELNAME}/chat/completions"
        self.api_version = bot_config.GPT_APIVERSION
        self.access_token = bot_config.GPT_ACCESS_TOKEN

    def submit_query(self, query):
        conversation = [{"role": "user", "content": query}]
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.access_token}"
        }
        params = {'api-version': self.api_version}
        payload = {'messages': conversation}

        try:
            response = requests.post(self.endpoint_url, params=params, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except requests.HTTPError as http_err:
            return f"HTTP error occurred: {http_err}"
        except Exception as err:
            return f"An error occurred: {err}"

if __name__ == '__main__':
    chatbot = ChatbotAssistant()
    print("ChatGPT Assistant is running. Type something to begin a conversation.")
    while True:
        user_input = input("You: ")
        response = chatbot.submit_query(user_input)
        print("ChatGPT:", response)
