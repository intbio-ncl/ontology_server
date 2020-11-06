import rdflib

rdf_type = rdflib.RDF.type



def convert(fn):
    graph = rdflib.Graph()
    if graph is not None:
        graph.load(fn)
    


    output = fn.split(".")[0] + ".xml"
    return graph.serialize(destination=output, format="xml")


import sys
if __name__ == "__main__":
    convert(sys.argv[1])