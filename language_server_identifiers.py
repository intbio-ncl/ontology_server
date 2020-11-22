import rdflib

class LSIdentifiers:
    def __init__(self):
        self.namespace = "http://language_server/"

        self.predicate_download = rdflib.URIRef("http://language_server/downloadUrl")
        self.predicate_query = rdflib.URIRef("http://language_server/queryCode")
        self.predicate_namespace = rdflib.URIRef("http://language_server/namespace")
        self.predicate_rdf_type = rdflib.RDF.type

        self.object_ontology = rdflib.URIRef("http://language_server/Ontology")
        self.object_owl = rdflib.OWL
ls_identifiers = LSIdentifiers()