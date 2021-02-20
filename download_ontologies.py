
import os
import requests
from owlready2 import get_ontology

ontologies = [
    "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.owl"
    "https://raw.githubusercontent.com/BioPAX/specification/master/Level3/specification/biopax-level3.owl"
    "http://www.ebi.ac.uk/sbo/exports/Main/SBO_OWL.owl"
    "http://edamontology.org/EDAM.owl"
    "http://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl"
    "http://purl.obolibrary.org/obo/go.owl"
]

download_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"ontologies")
def download(self):
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