FROM python:3.9

# bullseye:  worked
# buster:    got an error "lsb_release: command not found"
# I don't know the reason
# https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files/chromium-browser-dbgsym_100.0.4896.127-0ubuntu0.18.04.1_amd64.ddeb
ARG VERSION=100.0.4896.127-0ubuntu0.18.04.1
ARG ARCH=arm64
ARG URLBASE=https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files
WORKDIR /opt/chromium
RUN wget ${URLBASE}/chromium-codecs-ffmpeg_${VERSION}_${ARCH}.deb \
 && wget ${URLBASE}/chromium-codecs-ffmpeg-extra_${VERSION}_${ARCH}.deb \
 && wget ${URLBASE}/chromium-browser_${VERSION}_${ARCH}.deb \
 && wget ${URLBASE}/chromium-chromedriver_${VERSION}_${ARCH}.deb \
 && apt-get update \
 && apt-get install -y ./chromium-codecs-ffmpeg_${VERSION}_${ARCH}.deb \
 && apt-get install -y ./chromium-codecs-ffmpeg-extra_${VERSION}_${ARCH}.deb \
 && apt-get install -y ./chromium-browser_${VERSION}_${ARCH}.deb \
 && apt-get install -y ./chromium-chromedriver_${VERSION}_${ARCH}.deb \
 && rm -rf /var/lib/apt/lists/*

# Install selenium
RUN pip install --upgrade pip \
 && pip install selenium

COPY . /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt
