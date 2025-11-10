from flask import Blueprint, render_template, request, redirect, url_for
from .services.dbpedia_client import search_resources, get_resource_properties, get_graph_data
from logging import getLogger

logger = getLogger(__name__)

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "").strip()
    results = search_resources(q) if q else []
    logger.info(f"Search results: {results}")
    return render_template("index.html", q=q, results=results)


@bp.route("/resource")
def view_resource():
    uri = request.args.get("uri", "")
    props = get_resource_properties(uri) if uri else []
    return render_template("resource.html", uri=uri, props=props)


@bp.route('/graph')
def graph():
    uri = request.args.get('uri','').strip()
    if not uri:
        return redirect(url_for('main.index'))
    nodes, links = get_graph_data(uri)
    return render_template('graph.html', uri=uri, nodes=nodes, links=links)
