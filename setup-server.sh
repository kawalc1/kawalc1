#!/bin/bash

# Check if running with sudo
if [ "$(id -u)" -ne 0 ]; then
  echo "Please run with sudo"
  exit
fi

# Install Docker
apt update
apt install -y docker.io

# Enable Docker to start on boot
systemctl enable docker

# Install OpenSSL (for self-signed certificate)
apt install -y openssl

#install docker-compose
apt install docker-compose

# Replace "<X" with your actual IP address
IP_ADDRESS="<X>"

# Set the document root location
DOCUMENT_ROOT="/var/www/html"

# Create a self-signed SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/conf.d/selfsigned.key -out /etc/nginx/conf.d/selfsigned.crt -subj "/C=US/ST=State/L=City/O=Organization/CN=${IP_ADDRESS}"

# Create Nginx configuration directory
mkdir -p /etc/nginx/conf.d

# Create Nginx configuration file
cat > /etc/nginx/conf.d/nginx.conf <<EOL
server {
    listen 80;
    server_name ${IP_ADDRESS};

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${IP_ADDRESS};

    ssl_certificate /etc/nginx/conf.d/selfsigned.crt;
    ssl_certificate_key /etc/nginx/conf.d/selfsigned.key;

    location / {
	     proxy_pass  http://127.0.0.1:8080/;
    }
}
EOL

git clone https://github.com/kawalc1/kawalc1.git

# Run Nginx container with restart policy
docker run -d --name nginx-container \
  --network host \
  -v /etc/nginx/conf.d:/etc/nginx/conf.d \
  -v ${DOCUMENT_ROOT}:/var/www/html \
  -p 80:80 -p 443:443 \
  --restart unless-stopped \
  nginx

echo "Setup completed. Nginx is running with a self-signed SSL certificate for the specified IP address (${IP_ADDRESS}). Document root is set to ${DOCUMENT_ROOT}. Docker is set to start on boot."