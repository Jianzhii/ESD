FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt yahoo_friend.reqs.txt ./
RUN pip install --no-cache-dir -r http.reqs.txt -r yahoo_friend.reqs.txt
COPY ./python/yahoo_friend.py .
CMD [ "python", "./yahoo_friend.py" ]
