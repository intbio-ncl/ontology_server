import requests
import os
import rdflib
import atexit
from owlready2 import get_ontology
from SPARQLWrapper import SPARQLWrapper

default_ontologies = [
    "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.owl",
    "https://raw.githubusercontent.com/BioPAX/specification/master/Level3/specification/biopax-level3.owl",
    "http://www.ebi.ac.uk/sbo/exports/Main/SBO_OWL.owl",
    "http://edamontology.org/EDAM.owl",
    "http://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl",
    "http://purl.obolibrary.org/obo/go.owl"
]
external_ontologies_ns = "http://www.language_server.com/external_ontologies#"
download_predicate = rdflib.URIRef("http://www.language_server.com/external_ontologies/download_url")


graph_store = os.path.join(os.path.dirname(os.path.realpath(__file__)),"graph_store")
download_dir = os.path.join(graph_store,"ontologies")
ontology_graph = os.path.join(graph_store,"ontologies.xml")
base_server_uri = "http://localhost:8890/sparql"


class LanguageServer:
    def __init__(self):
        if not os.path.isfile(ontology_graph):
            self.ontology_graph = self.generate_new_ontology_graph()
        else:
            self.ontology_graph = rdflib.Graph()
            self.ontology_graph.load(ontology_graph)
        self.ontologies = {}
        pattern = (None,download_predicate,None)
        for s,p,o in self.ontology_graph.triples(pattern):
            o = OntologyResource(o)
            self.ontologies[os.path.basename(s)] = o
        
        self.sparql = SPARQLWrapper(base_server_uri)
        atexit.register(self._save_ontology_graph)

    def select(self,query):
        results = []
        # Need to mediate to the correct ontology.
        query_string = self.ontologies[default_ontologies[0]].build_query()
        sparql.setQuery(query_string)
        try :
            ret = sparql.queryAndConvert()
            print(ret)
        except Exception as e:
            print(e)
            pass

        return results
        
    def add_ontology(self,ontology):
        self._add_to_ontology_graph(ontology)
        ontology_res = OntologyResource(ontology)
        self.ontologies[os.path.basename(ontology)] = ontology_res

    def generate_new_ontology_graph(self):
        if not os.path.exists(graph_store):
            os.makedirs(graph_store)
        g = rdflib.Graph()
        for ontology in default_ontologies:
            name = os.path.basename(ontology).split(".")[0]
            s = rdflib.URIRef(external_ontologies_ns + name)
            g.add((s,download_predicate,rdflib.URIRef(ontology)))
        g.serialize(destination=ontology_graph, format="xml")
        return g

    def _add_to_ontology_graph(self,ontology):
        name = os.path.basename(ontology).split(".")[0]
        s = rdflib.URIRef(external_ontologies_ns + name)
        self.ontology_graph.add((s,download_predicate,rdflib.URIRef(ontology)))

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
        
        sparql = SPARQLWrapper("http://example.org/sparql")
    
    def build_query(self):
        query_string = "SELECT * WHERE { ?s ?p ?o. }"
        return query_string

    def download(self):
        r = requests.get(self.download_uri)
        r.raise_for_status()
        output_fn = os.path.join(download_dir,os.path.basename(self.download_uri))
        if os.path.isfile(output_fn):
            os.remove(output_fn)
        with open(output_fn,"a+") as f:
            f.write(r.text)
        onto = get_ontology(output_fn).load()
        onto.save(file = self.file_location, format = "rdfxml")
        os.remove(output_fn)

if __name__ == "__main__":
    server = LanguageServer()

