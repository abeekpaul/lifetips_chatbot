import requests
import aws_params

class HKBU_ChatGPT:
    def __init__(self):
        self.telegram_token = aws_params.TG_ACCESS_TOKEN
        self.basic_url = aws_params.GPT_BASICURL
        self.model_name = aws_params.GPT_MODELNAME
        self.api_version = aws_params.GPT_APIVERSION
        self.access_token = aws_params.GPT_ACCESS_TOKEN

        # rest of your code

    def submit(self, message):
        conversation = [{"role": "user", "content": message}]
        url = self.basic_url + "/deployments/" + self.model_name + "/chat/completions/?api-version=" + self.api_version
        headers = {'Content-Type': 'application/json', 'api-key': self.access_token}
        payload = {'messages': conversation}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response

if __name__ == '__main__':
    ChatGPT_test = HKBU_ChatGPT()
    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)