eval $(docker-machine env kawalc1-prod-1)
docker stop kawalc1
docker run --name kawalc1 -d -p 80:8000 sjappelodorus/kawalc1