import json

#yeah so what exactly are we doing in this config file?
# well the plan is to create a config that can load json files and do shit with them
# so how do we do that? do we want to create a general json thing or what
# well we could have it so that the json file is formatted to have options in it or that we pass certain information about it
# idk man how weill we do it
# we can figure it out along the way
# maybe.
class Config():
    def __init__(self, JSON_file):
        self.name = JSON_file
        self.load()
    def load(self):
        try:
            with open(self.name, 'r') as f:
                self._db = json.load(f)
        except FileNotFoundError:
            print(f"File not found! ../JSONs/{self.name}")
            self._db = {}

    def get(self, key, *args):
        # Retrieves a config entry
        return self._db.get(str(key), *args)

    def put(self, key, value):
        with open(self.name, 'w') as f:
            self._db[str(key)] = value
            json.dump(self._db, f, indent=4)
    def dump(self, all_data):
        with open(self.name, 'w') as f:
            self._db = all_data
            json.dump(self._db, f, indent=4)

    def pop(self, key):
        self._db.pop(str(key))
        with open(self.name, 'w') as f:
            json.dump(self._db, f, indent=4)

    def __contains__(self, item):
        return str(item) in self._db
    def __getitem__(self, item):
        try:
            return self._db[str(item)]
        except KeyError:
            raise KeyError
    def __len__(self):
        return len(self._db)
    def __setitem__(self, key, value):
        self.put(key,value)
    def all(self):
        return self._db

class ReadOnlyConfig():
    def __init__(self, JSON_file):
        self.name = JSON_file
        self.load()
    def load(self):
        try:
            with open(self.name, 'r') as f:
                self._db = json.load(f)
        except FileNotFoundError:
            print(f"File not found! ../JSONs/{self.name}")
            self._db = {}

    def get(self, key, *args):
        # Retrieves a config entry
        return self._db.get(str(key), *args)

    def __contains__(self, item):
        return str(item) in self._db
    def __getitem__(self, item):
        try:
            return self._db[str(item)]
        except KeyError:
            raise KeyError
    def __len__(self):
        return len(self._db)
    def all(self):
        return self._db
