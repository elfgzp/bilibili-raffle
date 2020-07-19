FROM python:3.6-slim
ADD ./requirements.txt /
RUN pip3 install -r requirements.txt
ADD . /
WORKDIR /
CMD [ "python3", "./main_raffle.py" ]
