from flask import Flask, render_template

from app import macro_collections
from config import SECRET_KEY


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


from app.auth import auth_blueprint
app.register_blueprint(auth_blueprint)

from app.home import home_blueprint
app.register_blueprint(home_blueprint)

from app.collection import collection_blueprint
app.register_blueprint(collection_blueprint)

from app.search import search_blueprint
app.register_blueprint(search_blueprint)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html")


app.jinja_env.globals.update(macro_collections=macro_collections)

app.run(debug=True)
