import pytest
import sqlite3
from app import app
from create_table import create_db


class TestAutoCompleter:

    URL = 'http://127.0.0.1:5000/'
    EXPECTED = {'options': [['aa'], ['azz']]}
    REQUESTED_OPTIONS_QUERY = "SELECT prefix, count FROM options WHERE is_word=1 AND prefix='aa' OR prefix='aaa' OR prefix='azz'"
    NEW_OPTIONS = {"aaa": 3, "aa": 10, "azz": 4}

    @pytest.fixture
    def client(self):
        return app.test_client()

    def test_add_options(self, client):
        create_db()
        con = sqlite3.connect('data.db')
        cur = con.cursor()
        expected = {"options": []}
        options = [row for row in cur.execute(TestAutoCompleter.REQUESTED_OPTIONS_QUERY).fetchall()]
        if options:
            expected["options"] = sorted([[option[0], option[1] + TestAutoCompleter.NEW_OPTIONS[option[0]]] for option in options], key=lambda x: x[1], reverse=True)
        else:
            expected["options"] = sorted([[option[0], option[1]] for option in TestAutoCompleter.NEW_OPTIONS.items()], key=lambda x: x[1], reverse=True)
        new_options = [[word, count] for word, count in TestAutoCompleter.NEW_OPTIONS.items()]
        response = client.post(TestAutoCompleter.URL, json=new_options)
        assert sorted(response.get_json()['options'], key=lambda x: x[1], reverse=True) == expected['options']

    def test_type_character(self, client):
        response = client.get(TestAutoCompleter.URL, json={'prefix': 'a', 'max_recommendations': 2})
        assert response.get_json() == TestAutoCompleter.EXPECTED

    def test_delete_character(self, client):
        response = client.delete(TestAutoCompleter.URL, json={'prefix': 'aa', 'max_recommendations': 2})
        assert response.get_json() == TestAutoCompleter.EXPECTED

    def test_delete_character_empty_prefix(self, client):
        response = client.delete(TestAutoCompleter.URL, json={'prefix': '', 'max_recommendations': 2})
        assert response.get_json() == {'options': []}
