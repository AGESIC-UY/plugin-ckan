#!/usr/bin/env bash
set -e

apt update -y
apt install -y locales
sed -i "/$LC_ALL/s/^# //g" /etc/locale.gen
echo "LC_ALL=$LC_ALL" > /etc/default/locale
dpkg-reconfigure --frontend=noninteractive locales
update-locale LANG=${LC_ALL}

# Install required system packages
DEBIAN_FRONTEND=noninteractive apt -q -y dist-upgrade \
    && apt -q -y install \
        python3-dev \
        python3-pip \
        libpq-dev \
        libxml2-dev \
        libxslt-dev \
        libgeos-dev \
        libssl-dev \
        libffi-dev \
        postgresql-client \
        build-essential \
        bash \
        git \
        libpcre3 \
        libpcre3-dev \
        vim \
        curl \
        iputils-ping \
        telnet \
        wget \
        mc \
    && apt -q clean \
    && rm -rf /var/lib/apt/lists/*
