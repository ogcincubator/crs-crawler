FROM python:3.12-alpine

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt \
    && wget https://github.com/ogcincubator/crs-crawler/raw/refs/heads/master/crs-list.txt

COPY main.py .

ENV ROOT_PATH=""
ENV FORWARDED_ALLOW_IPS="127.0.0.1"

CMD ["fastapi", "run", "main.py", "--proxy-headers", "--port", "8080", "--root-path", "${ROOT_PATH}"]