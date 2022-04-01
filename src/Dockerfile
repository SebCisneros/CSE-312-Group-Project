FROM python:3.10
ENV HOME /root
WORKDIR /root
COPY . .
RUN pip3 install pymongo

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD python3 app.py