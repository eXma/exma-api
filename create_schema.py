import sqlalchemy.exc
from sqlalchemy_schemadisplay import create_uml_graph
from sqlalchemy.orm import class_mapper
import db_backend.mapping

def fetch_mappers():
    # lets find all the mappers in our model
    mappers = []
    for attr in dir(db_backend.mapping):
        if attr[0] == '_': continue
        try:
            cls = getattr(db_backend.mapping, attr)
            mappers.append(class_mapper(cls))
        except Exception as ex:
            if isinstance(ex, sqlalchemy.exc.InvalidRequestError):
                if str(ex).startswith("One or more mappers failed to initialize"):
                    raise
            print("ignoring %s" % attr)
    return mappers


def make_graph(mappers):
    # pass them to the function and set some formatting options
    graph = create_uml_graph(mappers,
        show_operations=True, # not necessary in this case
        show_multiplicity_one=True # some people like to see the ones, some don't
    )
    return graph

mappers = fetch_mappers()
graph = make_graph(mappers)

graph.write_png('sqlalchemy-schemadisplay.png') # write out the file
graph.write_svg('sqlalchemy-schemadisplay.svg') # write out the file
