#!/usr/bin/env bash
sudo snap install docker

export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update && sudo apt-get install google-cloud-sdk

sudo docker rmi sjappelodorus/kawalc1:latest
sudo docker run --rm --name kawalc1 -p 8001:8000 -v /home/kawal:/root/creds -e GOOGLE_APPLICATION_CREDENTIALS=/root/creds/kawalc1-google-credentials.json sjappelodorus/kawalc1:latest

gcloud auth application-default login