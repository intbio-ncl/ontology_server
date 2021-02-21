python3.6 download_ontologies.py
systemctl start docker
docker build -t ontology_server .
docker volume create ontology_server_volume
sudo docker cp ontologies/ ontology_server_db_1:/data

