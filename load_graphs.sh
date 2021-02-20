
sudo docker cp ../graph_store/ontologies/ 794e1609b99e:/data
sudo docker exec -it server_db_1 /bin/bash 
isql-v -U dba

