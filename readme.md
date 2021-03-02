# Ontology Server
    A virtuoso server instance built specifically for quick and general access to a number of biological ontologies.


# Example SPARQL Queries
    SPARQL SELECT * FROM <graph_iri> WHERE {?s ?p ?o};       (Test the graph is loaded)
    SPARQL SELECT DISTINCT ?g WHERE { GRAPH ?g {?s a ?t}}    (Return all graph names)
    SPARQL CLEAR GRAPH <graph_iri>;						     (Deletes graph, need <>)

# Load Graphs
    isql-v -U dba
    DB.DBA.RDF_LOAD_RDFXML_MT (file_to_string_output ('ontologies/EDAM.owl'), '', 'http://ontology_server/EDAM');
    DB.DBA.RDF_LOAD_RDFXML_MT (file_to_string_output ('ontologies/SBO_OWL.owl'), '', 'http://ontology_server/SBO');
    DB.DBA.RDF_LOAD_RDFXML_MT (file_to_string_output ('ontologies/biopax-level3.owl'), '', 'http://ontology_server/biopax-level3');
    DB.DBA.RDF_LOAD_RDFXML_MT (file_to_string_output ('ontologies/chebi_lite.owl'), '', 'http://ontology_server/CHEBI');
    DB.DBA.RDF_LOAD_RDFXML_MT (file_to_string_output ('ontologies/go.owl'), '', 'http://ontology_server/GO');
    DB.DBA.RDF_LOAD_RDFXML_MT (file_to_string_output ('ontologies/so.owl'), '', 'http://ontology_server/SO');
