import os
import re
import atexit
from urllib.error import URLError
import rdflib
from aenum import extend_enum
from SPARQLWrapper import SPARQLWrapper,JSON

from .utility.identifiers import ls_identifiers
from .utility.ontology_enum import OntologyEnum
from .utility.ontology_resource import OntologyResource
from .utility.prepared_query import PreparedQuery

graph_store = os.path.join(os.path.dirname(os.path.realpath(__file__)),"graph_store")

ontology_graph = os.path.join(graph_store,"ontologies.xml")
base_server_uri = "http://localhost:8890/sparql"

class LanguageServer:
    def __init__(self):
        self.sparql = SPARQLWrapper(base_server_uri)
        if not os.path.isfile(ontology_graph):
            self.ontology_graph = self.generate_new_ontology_graph()
        else:
            self.ontology_graph = rdflib.Graph()
            self.ontology_graph.load(ontology_graph)

        self.prepared_queries = PreparedQuery
        atexit.register(self._save_ontology_graph)
        self._populate_enum()
        
    def select(self,query,ontology_name = None ,query_code = None,limit=None,filters=[]):
        results = []
        ontology_resources = self._get_ontology_resources(query,ontology_name,query_code)
        for ontology_resource in ontology_resources:
            query_string = ontology_resource.build_select(query,filters=filters)
            if limit is not None:
                query_string = f'{query_string} LIMIT {str(limit)}'
            result = self._run_query(query_string)
            if result is not None:
                results = results + result["results"]["bindings"]
        return results
    
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
            s = rdflib.URIRef(ls_identifiers.namespace + ontology.value.query_code)
            g.add((s,ls_identifiers.predicate_rdf_type,ls_identifiers.object_ontology))
            g.add((s,ls_identifiers.predicate_download,rdflib.URIRef(ontology.value.download_uri)))
            g.add((s,ls_identifiers.predicate_query,rdflib.Literal(ontology.value.query_code)))

            # Add The URI's
            ontology_qry = (None,ls_identifiers.predicate_rdf_type,ls_identifiers.object_owl + "Ontology")
            ontology_uri = self.select(ontology_qry,ontology_name=ontology.name,limit=None)[0]["s"]["value"]
            classes_qry = (None,ls_identifiers.predicate_rdf_type,ls_identifiers.object_owl + "Class")
            classes = self.select(classes_qry,ontology_name=ontology.name,limit=10)
            common_prefix = ""
            for c in classes:
                c = c["s"]["value"]
                cpx = os.path.commonprefix([ontology_uri,c])
                if len(cpx) > len(common_prefix):
                    common_prefix = cpx
            if common_prefix[-1] in "#\/":
                common_prefix = common_prefix[:-1]
            g.add((s,ls_identifiers.predicate_namespace,rdflib.URIRef(common_prefix)))
        return g

    def get_name(self,subject):
        split_subject = self.split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def split(self,uri):
        return re.split('#|\/|:', str(uri))
     
    def get_query_code(self,pattern):
        for identifier in pattern:
            if identifier is None:
                continue
            query_code = self.split(identifier)[-2]
            if query_code in [o.value.query_code for o in OntologyEnum]:
                return query_code
        raise ValueError(f'{pattern} is not a valid query for this server.')

    def get_all_query_codes(self):
        return [e.value.query_code for e in OntologyEnum]

    def _run_query(self,query_string):
        try:
            self.sparql.setQuery(query_string)
            self.sparql.setReturnFormat(JSON)
            ret = self.sparql.query()
            ret = ret.convert()
            return ret
        except URLError:
            return None

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
        for ontology in self.ontology_graph.triples((None,ls_identifiers.predicate_rdf_type,ls_identifiers.object_ontology)):
            name = self.get_name(ontology[0])
            if name in [e.value.query_code for e in OntologyEnum]:
                continue
            try:
                download_uri = next(self.ontology_graph.triples((ontology[0],ls_identifiers.predicate_download,None)))[2]
                query_code = next(self.ontology_graph.triples((ontology[0],ls_identifiers.predicate_query,None)))[2]
            except StopIteration:
                raise ValueError(f'Graph object: {ontology[0]} is not correctly formed.')
            o = OntologyResource(query_code,download_uri)
            extend_enum(OntologyEnum, name, o)

    def _save_ontology_graph(self):
        if not os.path.exists(graph_store):
            os.makedirs(graph_store)
        for ontology in OntologyEnum:
            s = rdflib.URIRef(ls_identifiers.namespace + ontology.value.query_code)
            try:
                next(self.ontology_graph.triples((s,None,None)))
            except StopIteration:
                self.ontology_graph.add((s,ls_identifiers.predicate_rdf_type,ls_identifiers.object_ontology))
                self.ontology_graph.add((s,ls_identifiers.predicate_download,rdflib.URIRef(ontology.value.download_uri)))
                self.ontology_graph.add((s,ls_identifiers.predicate_query,rdflib.URIRef(ontology.value.query_code)))
        return self.ontology_graph.serialize(destination=ontology_graph, format="xml")










