import requests

from flask import render_template, request, flash, url_for, redirect

from . import search_blueprint as bp
from security import Token
from config import BASE_API_URL


@bp.route("/search", methods=['GET'])
@Token.access_token_required
def search_text():
    collection_id = request.args.get("collection")
    keywords = request.args.get("keywords")

    if collection_id and keywords:
        try:
            response = requests.get(BASE_API_URL + f'/collection/{collection_id}/search',
                                    headers=Token.get_header_access(), json={'search': keywords})
        except requests.exceptions.RequestException:
            return render_template("error.html")

        json = response.json()

        if 'error' in json:
            flash(json['error'])
            return redirect(url_for('home.home'))

        return render_template("result.html", results=json['solution'], keywords=keywords, collection_id=collection_id)

    if not collection_id:
        flash("You need to select one collection.")

    if not keywords:
        flash("You need to type some keywords")

    return redirect(url_for('home.home'))


@bp.route("/advanced", methods=['GET'])
@Token.access_token_required
def advanced():
    return render_template("advanced.html")


@bp.route("/advanced/search", methods=['GET'])
def advanced_search():
    collection_id = request.args.get("collection")
    keywords = request.args.get("keywords")

    if collection_id and keywords:
        try:
            params = get_params_advanced(request.args)
            response = requests.get(BASE_API_URL + f'/collection/{collection_id}/search',
                                    headers=Token.get_header_access(), json={'search': keywords}, params=params)
        except requests.exceptions.RequestException:
            return render_template("error.html")

        json = response.json()

        if 'error' in json:
            flash(json['error'])
            return redirect(url_for('home.home'))

        return render_template("result.html", results=json['solution'], keywords=keywords, collection_id=collection_id)

    if not collection_id:
        flash("You need to select one collection.")

    if not keywords:
        flash("You need to type some keywords")

    return redirect(url_for('search.advanced'))


def get_params_advanced(args):
    return {
        'algorithm': args.get('algorithm'),
        'tf': args.get('tf'),
        'idf': args.get('idf'),
        'P': args.get('P')
    }
