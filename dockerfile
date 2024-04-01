FROM python:3.9-slim
WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80
ENV TELEGRAM_ACCESS_TOKEN="6903048598:AAGnNHA-om65R68Xj-W41BM0xRhmSnogfTU"
ENV CHATGPT_BASICURL="https://chatgpt.hkbu.edu.hk/general/rest"
ENV CHATGPT_MODELNAME="gpt-35-turbo"
ENV CHATGPT_APIVERSION="2024-02-15-preview"
ENV CHATGPT_ACCESS_TOKEN="c232a1f0-fb73-4308-a589-1085c9fd22c7"
ENV REDIS_HOST='redis-15520.c1.asia-northeast1-1.gce.cloud.redislabs.com'
ENV REDIS_PORT=15520
ENV REDIS_PASSWORD='BlsPHMJv1itLfwUOQNzpRbdOIgergLOG'

CMD ["python", "lifetips_chatbot.py"]