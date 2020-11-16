import requests
import os
import re
import rdflib
import atexit
from owlready2 import get_ontology
from SPARQLWrapper import SPARQLWrapper

default_ontologies = {
    "SO" : "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.owl",
    "biopax-level3" : "https://raw.githubusercontent.com/BioPAX/specification/master/Level3/specification/biopax-level3.owl",
    "SBO" : "http://www.ebi.ac.uk/sbo/exports/Main/SBO_OWL.owl",
    "EDAM" : "http://edamontology.org/EDAM.owl",
    #"CHEBI" : "http://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl",
    "GO" : "http://purl.obolibrary.org/obo/go.owl"
}
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
            o = OntologyResource(s,o)
            self.ontologies[self.get_name(s)] = o
        
        self.sparql = SPARQLWrapper(base_server_uri)
        atexit.register(self._save_ontology_graph)

    def select(self,query):
        results = []
        # Need to mediate to the correct ontology.
        print(query)
        query_string = self.ontologies["SO"].build_query()
        self.sparql.setQuery(query_string)
        try :
            ret = self.sparql.query()
            ret = ret.convert()
            print(ret)
        except Exception as e:
            print(e)
            pass

        return results

    def construct(self,query):
        '''
        Should we be using this instead??
        '''
        return None 
        
    def add_ontology(self,code,ontology):
        self._add_to_ontology_graph(code,ontology)
        ontology_res = OntologyResource(code,ontology)
        self.ontologies[code] = ontology_res

    def generate_new_ontology_graph(self):
        if not os.path.exists(graph_store):
            os.makedirs(graph_store)
        g = rdflib.Graph()
        for code,ontology in default_ontologies.items():
            s = rdflib.URIRef(external_ontologies_ns + code)
            g.add((s,download_predicate,rdflib.URIRef(ontology)))
        g.serialize(destination=ontology_graph, format="xml")
        return g

    def get_name(self,subject):
        split_subject = self.split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def split(self,uri):
        return re.split('#|\/|:', uri)

    def _add_to_ontology_graph(self,code,ontology):
        s = rdflib.URIRef(external_ontologies_ns + code)
        self.ontology_graph.add((s,download_predicate,rdflib.URIRef(ontology)))

    def _save_ontology_graph(self):
        return self.ontology_graph.serialize(destination=ontology_graph, format="xml")

class OntologyResource:
    def __init__(self,code,download_uri):
        self.download_uri = download_uri
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        self.file_location = os.path.join(download_dir,
                             os.path.basename(self.download_uri).split(".")[0] + ".xml")
        if not os.path.isfile(self.file_location):
            self.download()
            
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

