FROM python:3.9-slim
WORKDIR /app

COPY . /app

RUN pip install update
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD python lifetips_chatbot.py
