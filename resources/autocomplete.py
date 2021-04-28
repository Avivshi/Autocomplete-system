import sqlite3
from flask import request
from flask_restful import Resource
from models.autocomplete import AutoCompleteIndex, IncrementalAutoCompleteSearch


class AutoCompleteResource(Resource):

    def __init__(self):
        self.connector = sqlite3.connect('data.db')
        self.cursor = self.connector.cursor()

    def get(self):
        data = request.get_json()
        options = self.cursor.execute("SELECT prefix, count FROM options WHERE is_word=1")
        auto_complete_index = AutoCompleteIndex(options, False)
        auto_complete_search = IncrementalAutoCompleteSearch(auto_complete_index, data["max_recommendations"])
        return {"options": auto_complete_search.type_character(data["prefix"])}

    def post(self):
        options = request.get_json()
        AutoCompleteIndex(options)
        new_options = [row for row in self.cursor.execute("SELECT prefix, count FROM options WHERE is_word=1")]
        return {"options": new_options}

    def delete(self):
        data = request.get_json()
        options = self.cursor.execute("SELECT prefix, count FROM options WHERE is_word=1")
        auto_complete_index = AutoCompleteIndex(options, False)
        auto_complete_search = IncrementalAutoCompleteSearch(auto_complete_index, data["max_recommendations"])
        auto_complete_search.prefix = data["prefix"]
        return {"options": auto_complete_search.delete_character()}

    def __del__(self):
        self.connector.close()
