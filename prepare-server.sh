#!/usr/bin/env bash
sudo snap install docker

export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update && sudo apt-get install google-cloud-sdk

sudo docker rmi sjappelodorus/kawalc1:latest
sudo docker run --rm --name kawalc1 -p 8001:8000 -v /home/kawal:/root/creds -e GOOGLE_APPLICATION_CREDENTIALS=/root/creds/kawalc1-google-credentials.json sjappelodorus/kawalc1:latest

gcloud auth application-default login


sudo apt-get install software-properties-common
sudo apt-get install gcc python-dev python-setuptools
sudo apt-add-repository universe
sudo apt-get update
sudo apt-get install python-pip
sudo pip install --no-cache-dir -U crcmod

sudo docker run --rm --name kawalc1 -p 0.0.0.0:8001:8000 -v /home/kawal/output:/kawalc1/static/output -e TRANSFORMED_DIR=/kawalc1/static/output -e FORCE_LOCAL_FILE_SYSTEM=True -e GOOGLE_APPLICATION_CREDENTIALS=/root/creds/kawalc1-google-credentials.json sjappelodorus/kawalc1:latest

gsutil -m setmeta -h "Content-Type:image/webp" gs://kawalc1/**/*.webp

gcloud auth login

gsutil -m  rsync -r transformed gs://kawalc1/static/transformed