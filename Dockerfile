FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    bluez-tools \
    rfkill

EXPOSE 6000 50051

CMD ["python", "main.py", "--port", "/dev/tty0"]
