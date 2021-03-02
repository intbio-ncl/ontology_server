
import os
import urllib.request

ontologies = [
    "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.owl",
    "https://raw.githubusercontent.com/BioPAX/specification/master/Level3/specification/biopax-level3.owl",
    "http://www.ebi.ac.uk/sbo/exports/Main/SBO_OWL.owl",
    "http://edamontology.org/EDAM.owl",
    "ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl",
    "http://purl.obolibrary.org/obo/go.owl",
]


download_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"ontologies")
def download():
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
    for ontology in ontologies:
        owl_fn = os.path.join(download_dir,os.path.basename(ontology))
        if not os.path.isfile(owl_fn):
            with urllib.request.urlopen(ontology) as r:
                data = r.read()
            if os.path.isfile(owl_fn):
                os.remove(owl_fn)
            with open(owl_fn,"ba+") as f:
                f.write(data)


if __name__ == "__main__":download()
