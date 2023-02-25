FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install firefox-esr -y

CMD ["python", "beer_tracker.py"]