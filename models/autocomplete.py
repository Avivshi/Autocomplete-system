import sqlite3
from create_table import create_db


class TrieNode:
    def __init__(self, text=''):
        '''
        Initializes a TrieNode with the given string and an initially
        empty dictionary mapping strings to TrieNodes.
        '''
        self.text = text
        self.children = {}
        self.count = 0
        self.is_word = False


class AutoCompleteIndex(object):
    queries = {
        'insertion': "INSERT INTO options (prefix, count, is_word) VALUES (?, ?, ?)",
        'update': "UPDATE options SET count=?, is_word=? WHERE prefix=?",
        'existence_check': "SELECT prefix, count, is_word FROM options WHERE prefix LIKE ?",
        'prefixes': "SELECT prefix FROM options WHERE prefix LIKE ? and is_word=1 ORDER BY count DESC LIMIT ?"
    }

    def __init__(self, options, add_to_db=True):
        create_db()
        self.connection = sqlite3.connect("data.db")
        self.cursor = self.connection.cursor()
        self.root = TrieNode()
        self.add_to_db = add_to_db
        self.add_options(options)

    def add_options(self, options):
        for option in options:
            word, count = option
            row = self.cursor.execute(AutoCompleteIndex.queries['existence_check'], (word,)).fetchall()
            if row and self.add_to_db and row[0][0] == word:
                self.cursor.execute(AutoCompleteIndex.queries['update'], (row[0][1] + count, True, word))
            else:
                self.insert(option)

    def insert(self, option):
        node = self.root
        word, count = option
        for ind, letter in enumerate(word):
            if letter not in node.children:
                row = self.cursor.execute(AutoCompleteIndex.queries['existence_check'], (node.text,)).fetchall()
                node.children[letter] = TrieNode(option[0][:ind + 1])
                if self.add_to_db and not row:
                    self.cursor.execute(AutoCompleteIndex.queries['insertion'], (node.text, node.count, False))
            node = node.children[letter]
        node.count = count
        node.is_word = True
        if self.add_to_db:
            self.cursor.execute(AutoCompleteIndex.queries['insertion'], (node.text, node.count, node.is_word))

    def starts_with(self, prefix, max_recommendations):
        return [row for row in self.cursor.execute(AutoCompleteIndex.queries['prefixes'], (prefix+'%', max_recommendations))]

    def __del__(self):
        self.connection.commit()
        self.connection.close()


class IncrementalAutoCompleteSearch(object):

    def __init__(self, auto_complete_index, max_recommendations):
        self.auto_complete_index = auto_complete_index
        self.max_recommendations = max_recommendations
        self.prefix = ''

    def type_character(self, c):
        self.prefix += c
        return self.auto_complete_index.starts_with(self.prefix, self.max_recommendations)

    def delete_character(self):
        if len(self.prefix) > 1:
            self.prefix = self.prefix[:-1]
            return self.auto_complete_index.starts_with(self.prefix, self.max_recommendations)
        else:
            self.prefix = ''
            return []


if __name__ == "__main__":
    options = [('aa', 10), ('aaa', 3), ('azz', 4)]
    auto_complete_index = AutoCompleteIndex(options)
    auto_complete_search = IncrementalAutoCompleteSearch(auto_complete_index, max_recommendations=2)
    print(auto_complete_search.type_character('a'))  # --> ['aa', 'azz']
    print(auto_complete_search.type_character('a'))  # --> ['aa', 'aaa']
    print(auto_complete_search.delete_character())  # --> ['aa', 'azz']
    print(auto_complete_search.type_character('z'))  # --> ['azz']
    print(auto_complete_search.type_character('p'))  # --> []