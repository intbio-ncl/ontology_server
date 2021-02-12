import os
import requests

from owlready2 import get_ontology
import re

from .prepared_query import PreparedQuery
from .identifiers import ls_identifiers

graph_store = os.path.join(os.path.dirname(os.path.realpath(__file__)),"graph_store")
download_dir = os.path.join(graph_store,"ontologies")
class OntologyResource:
    def __init__(self,query_code,download_uri):
        self.query_code = query_code
        self.server_uri = ls_identifiers.namespace + query_code + "/"
        self.download_uri = download_uri
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        self.file_location = os.path.join(download_dir,
                             os.path.basename(self.download_uri).split(".")[0] + ".xml")
        if not os.path.isfile(self.file_location):
            self.download()
            
    def build_select(self,pattern,filters=[]):
        s = f'<{str(pattern[0])}>' if pattern[0] is not None else "?s"
        p = f'<{str(pattern[1])}>' if pattern[1] is not None else "?p"
        o = f'<{str(pattern[2])}>' if pattern[2] is not None else "?o"
        SELECT = "?s ?p ?o"
        FROM = self.server_uri
        WHERE = f'{s} {p} {o}'
        query = PreparedQuery(SELECT,FROM,WHERE)
        for _filter in filters:
            query.add_filter(_filter)
        query_string = query.build()
        return query_string

    def download(self):
        print("Warn:: Stopped downloads on the ontology work")
        return
        r = requests.get(self.download_uri)
        r.raise_for_status()
        output_fn = os.path.join(download_dir,os.path.basename(self.download_uri))
        if os.path.isfile(output_fn):
            os.remove(output_fn)
        with open(output_fn,"a+",encoding="UTF-8") as f:
            f.write(r.text)
        onto = get_ontology(output_fn).load()
        onto.save(file = self.file_location, format = "rdfxml")
        os.remove(output_fn)