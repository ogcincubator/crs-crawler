FROM python:3.12-alpine

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt \
    && wget https://github.com/ogcincubator/crs-crawler/raw/refs/heads/master/crs-list.txt

COPY main.py .

CMD ["python3", "main.py"]
