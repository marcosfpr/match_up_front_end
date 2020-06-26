from flask import render_template, request, flash, redirect, url_for
import requests

from config import BASE_API_URL
from . import collection_blueprint as bp
from security import Token


@bp.route("/collection/<int:collection_id>", methods=['GET', 'POST', 'DELETE'])
@Token.access_token_required
def collection(collection_id):
    base_link = f"{BASE_API_URL}/collection/{collection_id}"

    if request.method == 'GET':
        try:
            collection_json = requests.get(base_link, headers=Token.get_header_access()).json()
            files_json = requests.get(base_link + "/filelist", headers=Token.get_header_access()).json()
        except requests.exceptions.RequestException:
            return render_template("error.html")

        return render_template("collection.html", collection=collection_json, files=files_json)

    elif request.method == 'POST':
        data = request.form
        request_data = {
            "name": data['name'],
            "description": data['description']
        }
        try:
            response = requests.put(BASE_API_URL + f'/collection/{collection_id}', headers=Token.get_header_access(),
                                    json=request_data)
        except requests.exceptions.RequestException:
            return render_template("error.html")

        json = response.json()

        if 'error' in json:
            flash("[ERROR] " + json['error'])
        elif 'success' in json:
            flash(json['success'])

        return redirect(request.url)

    elif request.method == 'DELETE':
        response = None
        try:
            response = requests.delete(BASE_API_URL + f"/collection/{collection_id}",
                                       headers=Token.get_header_access())
        except requests.exceptions.RequestException:
            flash("[ERROR] Unexpected error")

        if response:
            json = response.json()
            if 'error' in json:
                flash("[ERROR] " + json['error'])
            if 'success' in json:
                flash(json['success'])

        return "process finished"


@bp.route("/collection/<int:collection_id>/upload", methods=['POST'])
@Token.access_token_required
def upload_files(collection_id):

    file_up = request.files.getlist("file")

    for file in file_up:
        send_file = {"file": (file.filename, file.stream, file.mimetype)}
        try:
            response = requests.post(BASE_API_URL + f"/collection/{collection_id}/upload",
                                     headers=Token.get_header_access(), files=send_file)
        except requests.exceptions.RequestException:
            flash("[ERROR] Unexpected error.")
            return redirect(url_for("collection.collection", collection_id=collection_id))

        json = response.json()

        if 'error' in json:
            flash("[ERROR] " + json['error'])
        elif 'success' in json:
            flash(json['success'])

    return redirect(url_for("collection.collection", collection_id=collection_id))


@bp.route("/collection/<int:collection_id>/<string:filename>", methods=['GET', 'DELETE'])
@Token.access_token_required
def manage_collection_file(collection_id, filename):
    response = None
    if request.method == 'GET':
        try:
            response = requests.get(BASE_API_URL+f"/collection/{collection_id}/{filename}",
                                    headers=Token.get_header_access())
        except requests.exceptions.RequestException:
            flash("[ERROR] Unexpected error")

        file_content = response.text if response else "Unexpected error"
        return render_template('file-show.html', filename=filename, filecontent=file_content)

    try:
        response = requests.delete(BASE_API_URL + f"/collection/{collection_id}/{filename}",
                                   headers=Token.get_header_access())
    except requests.exceptions.RequestException:
        flash("[ERROR] Unexpected error")

    if response:
        json = response.json()
        if 'error' in json:
            flash("[ERROR] " + json['error'])
        if 'success' in json:
            flash(json['success'])

    return "finished process"


@bp.route("/collection/register", methods=['GET', 'POST'])
@Token.access_token_required
def register_collection():

    if request.method == 'GET':
        return render_template("collection_register.html")

    data = request.form
    request_data = {
        "name": data['name'],
        "description": data['description']
    }
    try:
        response = requests.post(BASE_API_URL + '/collection', headers=Token.get_header_access(),
                                 json=request_data)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'error' in json:
        flash("[ERROR] " + json['error'])
        return redirect(request.url)
    elif 'success' in json:
        flash(json['success'])

    return redirect(url_for('home.home'))


@bp.route("/collection/<int:collection_id>/process", methods=['GET'])
@Token.access_token_required
def process_collection(collection_id):
    try:
        response = requests.get(BASE_API_URL+f"/collection/{collection_id}/process",
                                headers=Token.get_header_access())
    except requests.exceptions.RequestException:
        flash("[ERROR] Unexpected error")
        return render_template("error.html")

    json = response.json()
    if 'error' in json:
        flash("[ERROR] " + json['error'])
    if 'success' in json:
        flash(json['success'])

    return "collection processed"
