Process for the server going from nothing to running with graphs loaded. (Manual)

1. sudo /usr/local/bin/docker-compose up							(Launch the server)
2. sudo docker cp ontologies/ 794e1609b99e:/data						(Copies the locally stored ontologies to the docker volume)
3. sudo docker exec -it server_db_1 /bin/bash							(Runs the command /bin/bash in the container server_db_1)
4. isql-v -U dba										(Launches isql)
5  DB.DBA.RDF_LOAD_RDFXML_MT (file_to_string_output ('ontology_file.xml'), '', '<graph_iri>');	(Load the graphs)
6. sparql select *
	  from <http://example.com>
	  where {?s ?p ?o};									(Test the graph is loaded)

7. SPARQL
   SELECT DISTINCT ?g 
   WHERE { GRAPH ?g {?s a ?t}}									(Return all graph names)






Misc Commands
1. SPARQL CLEAR GRAPH <graph_iri>;								(Deletes graph, need <>)
