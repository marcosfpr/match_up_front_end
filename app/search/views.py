import requests

from flask import render_template, request, flash, url_for, redirect

from . import search_blueprint as bp
from security import Token
from config import BASE_API_URL


@bp.route("/search/file", methods=['GET'])
@Token.access_token_required
def file():
    return render_template("search-file.html")


@bp.route("/search", methods=['GET'])
@Token.access_token_required
def search_text():
    collection_id = request.args.get("collection")
    keywords = request.args.get("keywords")

    kwargs = dict()

    if collection_id and keywords:
        return search(collection_id, keywords=keywords)

    if not collection_id:
        flash("[ERROR] You need to select one collection.")
        if keywords:
            kwargs['keywords'] = keywords

    if not keywords:
        flash("[ERROR] You need to put some input.")
        if collection_id:
            kwargs['collection_id'] = int(collection_id)

    return render_template('index.html', **kwargs)


@bp.route("/search/file", methods=['POST'])
@Token.access_token_required
def search_file():
    data = request.form
    collection_id = data.get("collection")
    file_up = request.files.getlist("file")

    kwargs = dict()

    if collection_id:
        for f in file_up:
            if f.filename:
                send_file = (f.filename, f.stream, f.mimetype)
                return search(collection_id, file_search=send_file)
            else:
                flash("[ERROR] You need to put one file.")
                if collection_id:
                    kwargs['collection_id'] = int(collection_id)
                break

    if not collection_id:
        flash("[ERROR] You need to select one collection.")

    return render_template("search-file.html", **kwargs)


def search(collection_id, *, keywords=None, file_search=None):
    try:
        if keywords:
            response = requests.get(BASE_API_URL + f'/collection/{collection_id}/search',
                                    headers=Token.get_header_access(), json={'search': keywords})
        else:
            response = requests.get(BASE_API_URL + f'/collection/{collection_id}/search',
                                    headers=Token.get_header_access(), files={'file': file_search})
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'error' in json:
        flash("[ERROR] " + json['error'])
        return redirect(url_for('home.home'))

    return render_template("result.html", results=json['solution'], keywords=keywords if keywords else file_search[0],
                           collection_id=collection_id)


@bp.route("/advanced", methods=['GET'])
@Token.access_token_required
def advanced():
    return render_template("advanced.html")


@bp.route("/advanced/search", methods=['GET'])
@Token.access_token_required
def advanced_text():
    collection_id = request.args.get("collection")
    keywords = request.args.get("keywords")

    kwargs = dict()

    params = get_params_advanced(request.args)

    if collection_id and keywords:
        try:
            response = requests.get(BASE_API_URL + f'/collection/{collection_id}/search',
                                    headers=Token.get_header_access(), json={'search': keywords}, params=params)
        except requests.exceptions.RequestException:
            return render_template("error.html")

        json = response.json()

        if 'error' in json:
            flash("[ERROR] " + json['error'])
            return render_template("advanced.html", collection_id=collection_id, keywords=keywords, params=params)

        return render_template("result.html", results=json['solution'], keywords=keywords, collection_id=collection_id)

    if not collection_id:
        flash("[ERROR] You need to select one collection.")
        if keywords:
            kwargs['keywords'] = keywords

    if not keywords:
        flash("[ERROR] You need to type some keywords")
        if collection_id:
            kwargs['collection_id'] = int(collection_id)

    kwargs['params'] = params

    return render_template("advanced.html", **kwargs)


@bp.route("/advanced/file", methods=['GET', 'POST'])
@Token.access_token_required
def advanced_with_file():
    if request.method == 'GET':
        return render_template('advanced-search-file.html')
    else:
        data = request.form
        collection_id = data.get("collection")
        file_up = request.files.getlist("file")

        params = get_params_advanced(data)
        kwargs = dict()

        if collection_id:
            for f in file_up:
                if f.filename:
                    try:
                        file_search = (f.filename, f.stream, f.mimetype)
                        response = requests.get(BASE_API_URL + f'/collection/{collection_id}/search',
                                                headers=Token.get_header_access(), files={'file': file_search},
                                                params=params)
                    except requests.exceptions.RequestException:
                        return render_template("error.html")

                    json = response.json()

                    if 'error' in json:
                        flash("[ERROR] " + json['error'])
                        return render_template("advanced-search-file.html", collection_id=collection_id, params=params)

                    return render_template("result.html", results=json['solution'], keywords=f.filename,
                                           collection_id=collection_id)
                else:
                    flash("[ERROR] You need to put one file.")
                    if collection_id:
                        kwargs['collection_id'] = int(collection_id)
                    break

        if not collection_id:
            flash("[ERROR] You need to select one collection.")

        kwargs['params'] = params

        return render_template('advanced-search-file.html', **kwargs)


def get_params_advanced(args):
    return {
        'algorithm': args.get('algorithm'),
        'tf': args.get('tf'),
        'idf': args.get('idf'),
        'P': args.get('P'),
        'K': args.get('K')
    }
