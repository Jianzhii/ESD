FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt amqp.reqs.txt ./
RUN pip install --no-cache-dir -r http.reqs.txt -r amqp.reqs.txt
COPY ./python/order_management.py ./python/invokes.py ./python/invokes.py ./python/amqp_setup.py ./
CMD [ "python", "./order_management.py" ]