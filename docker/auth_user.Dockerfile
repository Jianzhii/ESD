FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt google.reqs.txt amqp.reqs.txt ./
RUN pip install --no-cache-dir -r http.reqs.txt -r amqp.reqs.txt -r google.reqs.txt 
COPY ./python/authUser.py ./python/invokes.py ./python/amqp_setup.py ./
CMD [ "python", "./authUser.py" ]