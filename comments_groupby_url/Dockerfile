FROM python:3.9.7-slim
RUN pip install --upgrade pip && pip3 install pika

COPY comments_groupby_url /
COPY common /common
CMD ["python", "./main.py"]