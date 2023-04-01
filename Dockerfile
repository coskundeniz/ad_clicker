FROM python:3.10-slim-buster

# install required packages
RUN apt-get update && apt-get install -y wget gnupg

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable && rm -rf /var/lib/apt/lists/*

# Set the working directory to /src
WORKDIR /src

# upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip

# install dependencies
COPY ./requirements.txt /src
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the image
COPY . /src

# set display port to avoid crash
ENV DISPLAY=:99

# Start Xvfb
CMD Xvfb :99 -screen 0 1920x1080x16

ENTRYPOINT ["python"]
