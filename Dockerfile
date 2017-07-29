FROM python:2

WORKDIR /usr/src/app

COPY requirements_python2.txt ./
RUN pip install --no-cache-dir -r requirements_python2.txt

COPY . .

CMD [ "python", "./cardboardbot.py" ]

VOLUME /data
