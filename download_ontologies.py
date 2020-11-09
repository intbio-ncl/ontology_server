import requests
import os
import rdflib
import atexit


default_ontologies = [
    "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.owl",
    "https://raw.githubusercontent.com/BioPAX/specification/master/Level3/specification/biopax-level3.owl",
    "http://www.ebi.ac.uk/sbo/exports/Main/SBO_OWL.owl",
    "http://edamontology.org/EDAM.owl",
    #"http://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl",
    "http://purl.obolibrary.org/obo/go.owl"
]
external_ontologies_ns = "http://www.language_server.com/external_ontologies#"
download_predicate = rdflib.URIRef("http://www.language_server.com/external_ontologies/download_url")


graph_store = os.path.join(os.path.dirname(os.path.realpath(__file__)),"graph_store")
download_dir = os.path.join(graph_store,"ontologies")
ontology_graph = os.path.join(graph_store,"ontologies.xml")

class LanguageServer:
    def __init__(self):
        if not os.path.isfile(ontology_graph):
            self.generate_new_ontology_graph()
        
        self.ontology_graph = rdflib.Graph()
        self.ontology_graph.load(ontology_graph)
        self.ontologies = {}
        pattern = (None,download_predicate,None)
        for s,p,o in self.ontology_graph.triples(pattern):
            o = OntologyResource(o)
            self.ontologies[os.path.basename(s)] = o

        atexit.register(self._save_ontology_graph)

    def query(self,something,query):
        pass
        
    def add_ontology(self,ontology_download,identifier_prefixes):

        ontology = OntologyResource(ontology_download)
        self.ontologies[os.path.basename(ontology)] = ontology

    def generate_new_ontology_graph(self):
        if not os.path.exists(graph_store):
            os.makedirs(graph_store)
        g = rdflib.Graph()
        for ontology in default_ontologies:
            name = os.path.basename(ontology).split(".")[0]
            s = rdflib.URIRef(external_ontologies_ns + name)
            g.add((s,download_predicate,rdflib.URIRef(ontology)))
        return g.serialize(destination=ontology_graph, format="xml")

    def _save_ontology_graph(self):
        return self.ontology_graph.serialize(destination=ontology_graph, format="xml")

class OntologyResource:
    def __init__(self,download_uri):
        self.download_uri = download_uri
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        self.file_location = os.path.join(download_dir,
                             os.path.basename(self.download_uri).split(".")[0] + ".xml")
        if not os.path.isfile(self.file_location):
            self.download()
    
    def query(self):
        pass


    def download(self):
        r = requests.get(self.download_uri)
        r.raise_for_status()
        output_fn = os.path.join(download_dir,os.path.basename(self.download_uri))
        if os.path.isfile(output_fn):
            os.remove(output_fn)
        with open(output_fn,"a+") as f:
            f.write(r.text)
        graph = rdflib.Graph()
        if graph is not None:
            graph.load(output_fn)
        os.remove(output_fn)
        return graph.serialize(destination=self.file_location, format="xml")


if __name__ == "__main__":
    server = LanguageServer()

