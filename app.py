from flask import Flask
from flask_restful import Api
from create_table import create_db
from resources.autocomplete import AutoCompleteResource


app = Flask(__name__)
app.secret_key = "SECRET_KEY"
api = Api(app)


@app.before_first_request
def create_tables():
    create_db()


api.add_resource(AutoCompleteResource, '/')

if __name__ == "__main__":
    app.run(port=5000, debug=True)
