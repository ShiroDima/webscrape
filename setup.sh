#!/bin/bash

echo "############################################"
echo "Installing Redis-Server on this machine"
echo "############################################"

sudo apt install lsb-release curl gpg
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt-get update > /dev/null
sudo apt-get install redis > /dev/null

echo "############################################"
echo "Starting Redis server"
echo "############################################"

sudo systemctl restart redis-server
sudo systemctl enable redis-server

echo "############################################"
echo "Installing Python requirements"
echo "############################################"

pip install -r scrapers/requirements.txt > /dev/null

echo "############################################"
echo "Starting Celery"
echo "############################################"

celery -A crawler worker --beat --loglevel=INFO
