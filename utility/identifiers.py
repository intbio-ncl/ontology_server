import rdflib

class LSIdentifiers:
    def __init__(self):
        self.namespace = "http://language_server/"

        self.predicate_download = rdflib.URIRef(self.namespace + "downloadUrl")
        self.predicate_query = rdflib.URIRef(self.namespace + "queryCode")
        self.predicate_namespace = rdflib.URIRef(self.namespace + "namespace")
        self.predicate_rdf_type = rdflib.RDF.type

        self.object_ontology = rdflib.URIRef(self.namespace + "Ontology")
        self.object_owl = rdflib.OWL
        
ls_identifiers = LSIdentifiers()