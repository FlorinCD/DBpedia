from SPARQLWrapper import SPARQLWrapper, JSON

ENDPOINT = 'https://dbpedia.org/sparql'

sparql = SPARQLWrapper(ENDPOINT)

SEARCH_QUERY = """
PREFIX rdfs: < http: // www.w3.org / 2000 / 01 / rdf - schema  # >
SELECT DISTINCT ?resource ?label WHERE {
    ?resource rdfs: label ?label .
    FILTER(langMatches(lang(?label), 'EN') & & regex(str(?label), '%s', 'i'))
    } LIMIT 50
"""

PROPS_QUERY = """
SELECT ?p ?o WHERE {
    <%s> ?p ?o .
    } LIMIT 200
"""

GRAPH_QUERY = """
SELECT ?p ?o WHERE {
    <%s> ?p ?o .
    FILTER(isIRI(?o) || isLiteral(?o))
    } LIMIT 100
"""

def run_query(query):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def search_resources(term):
    if not term:
        return []
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?resource ?label WHERE {{
      ?resource rdfs:label ?label .
      FILTER (langMatches(lang(?label), "EN") && regex(str(?label), "{term}", "i"))
    }} LIMIT 50
    """
    data = run_query(query)
    return [
        {"uri": b["resource"]["value"], "label": b["label"]["value"]}
        for b in data["results"]["bindings"]
    ]


def get_resource_properties(uri):
    query = f"""
    SELECT ?p ?o WHERE {{
      <{uri}> ?p ?o .
    }} LIMIT 150
    """
    data = run_query(query)
    return [{"p": b["p"]["value"], "o": b["o"]["value"]} for b in data["results"]["bindings"]]


def get_graph_data(uri):
    q = GRAPH_QUERY % uri
    res = run_query(q)
    bindings = res.get('results', {}).get('bindings', [])
    nodes = [{'id': uri, 'label': uri.split('/')[-1]}]
    links = []
    seen = set([uri])
    for b in bindings:
        p = b['p']['value']
        o = b['o']['value']
        if o.startswith('http'):
            node_id = o
            label = o.split('/')[-1]
            if node_id not in seen:
                nodes.append({'id': node_id, 'label': label})
                seen.add(node_id)
            links.append({'source': uri, 'target': node_id, 'label': p})
    return nodes, links
