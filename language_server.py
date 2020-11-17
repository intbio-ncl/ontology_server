import requests
import os
import re
import rdflib
import atexit
from aenum import Enum,extend_enum
from owlready2 import get_ontology
from SPARQLWrapper import SPARQLWrapper,JSON

external_ontologies_ns = "http://language_server/ontology#"
ontology_object = rdflib.URIRef("http://language_server/Ontology")
download_predicate = rdflib.URIRef("http://language_server/downloadUrl")
query_code_predicate = rdflib.URIRef("http://language_server/queryCode")
graph_store = os.path.join(os.path.dirname(os.path.realpath(__file__)),"graph_store")
download_dir = os.path.join(graph_store,"ontologies")
ontology_graph = os.path.join(graph_store,"ontologies.xml")
base_server_uri = "http://localhost:8890/sparql"
rdf_type = rdflib.RDF.type

class LanguageServer:
    def __init__(self):
        if not os.path.isfile(ontology_graph):
            self.ontology_graph = self.generate_new_ontology_graph()
        else:
            self.ontology_graph = rdflib.Graph()
            self.ontology_graph.load(ontology_graph)
        atexit.register(self._save_ontology_graph)
        self._populate_enum()
        self.sparql = SPARQLWrapper(base_server_uri)

    def select(self,query,ontology_name = None ,query_code = None):
        results = []
        # Need to mediate to the correct ontology.
        ontology_resources = self._get_ontology_resources(query,ontology_name,query_code)
        for ontology_resource in ontology_resources:
            query_string = ontology_resource.build_query(query)
            result = self._run_query(query_string)
            print(result)
        return results

    def construct(self,query):
        '''
        Should we be using this instead??
        '''
        return None 
    

    def add_ontology(self,download_uri,query_code=None,name=None):
        if query_code is None:
            query_code = self.split(download_uri)[-1].split(".")[0]
        if name is None:
            name = query_code
        ontology_res = OntologyResource(query_code,download_uri)
        extend_enum(OntologyEnum, name, ontology_res)

    def generate_new_ontology_graph(self):
        g = rdflib.Graph()
        for ontology in OntologyEnum:            
            s = rdflib.URIRef(external_ontologies_ns + ontology.name)
            g.add((s,rdf_type,ontology_object))
            g.add((s,download_predicate,rdflib.URIRef(ontology.value.download_uri)))
            g.add((s,query_code_predicate,rdflib.Literal(ontology.value.query_code)))
        return g

    def get_name(self,subject):
        split_subject = self.split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def split(self,uri):
        return re.split('#|\/|:', uri)
    
    def _run_query(self,query_string):
        self.sparql.setQuery(query_string)
        self.sparql.setReturnFormat(JSON)
        ret = self.sparql.query()
        ret = ret.convert()
        return ret

    def _get_ontology_resources(self,query,ontology_name,query_code):
        ontology_resources = []
        if ontology_name is not None:
            if isinstance(ontology_name,OntologyEnum):
                ontology_resources = [ontology_name.value]
            else:
                ontology_resources = [o.value for o in OntologyEnum if o.name == ontology_name]
        elif query_code is not None:
            ontology_resources = OntologyEnum.get_enum_by_code(query_code)
        elif query[0] is not None:
            query_code = self.split(query[0])[-2]
            ontology_resources = OntologyEnum.get_enum_by_code(query_code)
        else:
            ontology_resources = [o.value for o in OntologyEnum]
        return ontology_resources

    def _populate_enum(self):
        for ontology in self.ontology_graph.triples((None,rdf_type,ontology_object)):
            name = self.get_name(ontology[0])
            if name in [e.name for e in OntologyEnum]:
                continue
            try:
                download_uri = next(self.ontology_graph.triples((ontology[0],download_predicate,None)))[2]
                query_code = next(self.ontology_graph.triples((ontology[0],query_code_predicate,None)))[2]
            except StopIteration:
                raise ValueError(f'Graph object: {ontology[0]} is not correctly formed.')
            o = OntologyResource(query_code,download_uri)
            extend_enum(OntologyEnum, name, o)

    def _save_ontology_graph(self):
        if not os.path.exists(graph_store):
            os.makedirs(graph_store)
        for ontology in OntologyEnum:
            s = rdflib.URIRef(external_ontologies_ns + ontology.name)
            try:
                next(self.ontology_graph.triples((s,None,None)))
            except StopIteration:
                self.ontology_graph.add((s,rdf_type,ontology_object))
                self.ontology_graph.add((s,download_predicate,rdflib.URIRef(ontology.value.download_uri)))
                self.ontology_graph.add((s,query_code_predicate,rdflib.URIRef(ontology.value.query_code)))
        return self.ontology_graph.serialize(destination=ontology_graph, format="xml")


class OntologyResource:
    def __init__(self,query_code,download_uri):
        self.query_code = query_code
        self.download_uri = download_uri
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        self.file_location = os.path.join(download_dir,
                             os.path.basename(self.download_uri).split(".")[0] + ".xml")
        if not os.path.isfile(self.file_location):
            self.download()
            
    def build_query(self,pattern):
        print(pattern)
        raise NotImplementedError("Youll have to rebuild the graph uri.")
        print(self.query_code)
        query_string = "SELECT * FROM  WHERE { ?s ?p ?o. }"
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

class OntologyEnum(Enum):
    SO = OntologyResource("SO","https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.owl")
    biopax_level3 = OntologyResource("biopax-level3.owl","https://raw.githubusercontent.com/BioPAX/specification/master/Level3/specification/biopax-level3.owl")
    SBO = OntologyResource("SBO","http://www.ebi.ac.uk/sbo/exports/Main/SBO_OWL.owl")
    EDAM = OntologyResource("EDAM","http://edamontology.org/EDAM.owl")
    CHEBI =  OntologyResource("CHEBI","http://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl")
    GO =  OntologyResource("GO","http://purl.obolibrary.org/obo/go.owl")
     
    @classmethod
    def get_enum_by_code(cls, code):
        matches = []
        for enum in cls:
            if enum.value.query_code == code:
                matches.append(enum.value)
        return matches


if __name__ == "__main__":
    server = LanguageServer()

