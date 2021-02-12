from aenum import Enum

from .ontology_resource import OntologyResource

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