sudo systemctl start docker
sudo /usr/local/bin/docker-compose up -d
sudo docker exec -it ontology_server_db_1 /bin/bash 
isql-v -U dba
