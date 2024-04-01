import requests
import bot_config  # Renamed aws_params to bot_config for clarity

class ChatbotAssistant:
    def __init__(self):
        self.telegram_token = bot_config.TELEGRAM_ACCESS_TOKEN
        self.endpoint_url = f"{bot_config.CHATGPT_BASE_URL}/deployments/{bot_config.CHATGPT_MODEL_NAME}/chat/completions"
        self.api_version = bot_config.CHATGPT_API_VERSION
        self.access_token = bot_config.CHATGPT_ACCESS_TOKEN

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
            response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
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
