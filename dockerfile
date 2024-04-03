FROM python:3.9-slim
WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80
<<<<<<< HEAD
<<<<<<< HEAD
=======
ENV TELEGRAM_ACCESS_TOKEN="6903048598:AAGnNHA-om65R68Xj-W41BM0xRhmSnogfTU"
ENV CHATGPT_BASICURL="https://chatgpt.hkbu.edu.hk/general/rest"
ENV CHATGPT_MODELNAME="gpt-35-turbo"
ENV CHATGPT_APIVERSION="2024-02-15-preview"
ENV CHATGPT_ACCESS_TOKEN="806d4871-36c3-4f74-ac4e-ba48560c0def"
ENV REDIS_HOST='LifeTips.redis.cache.windows.net'
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD='YzUKO7HUcdHQCZ6Ps0eb1EEF2Al1moJ0wAzCaJfIIEw='
>>>>>>> f131460 (update)

CMD python lifetips_chatbot.py
=======


CMD ["python", "lifetips_chatbot.py"]
>>>>>>> 8484a41 (fixed parameter access error)
