FROM python:3.6-slim
ADD . /
RUN pip3 install -r requirements.txt
WORKDIR /
CMD [ "python3", "./main_raffle.py" ]
