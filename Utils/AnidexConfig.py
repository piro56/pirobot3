import json
from fuzzywuzzy import fuzz
class AniConfig():
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
        self._db.pop([str(key)])
        with open(self.name, 'w') as f:
            json.dump(self._db, f, indent=4)

    def __contains__(self, item):
        for key in self._db.keys():
            if item.lower() in key.lower():
                return True
        return False
    # value, key
    def get_precise(self,item):
        if(self._db.get(item.title())):
            return self._db[item.title()], item.title()
        else:
            keys = []
            for key in self._db:
                keys.append({"key":key,"value" : fuzz.partial_ratio(item, key)})
            val = max(keys,key=lambda x : x['value'])["key"]
            return self._db[val], val
    def get_multiple(self,item, threshold = 75):
        keys = []
        to_return = []
        for key in self._db:
            keys.append({"key":key,"value" : fuzz.token_set_ratio(item, key)})
        for key in keys:
            if key["value"] > threshold:
                for db_item in self._db[key["key"]]:
                    to_return.append(db_item)
        return to_return
    def __getitem__(self, item):
        try:
            return self._db[str(item)]
        except KeyError:
            return False
    def __len__(self):
        return len(self._db)
    def __setitem__(self, key, value):
        self.put(key,value)
    def all(self):
        return self._db

class ReadOnlyAniConfig():
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
        for key in self._db.keys():
            if item.lower() in key.lower():
                return True
        return False
    def get_precise(self,item):
        keys = []
        for key in self._db:
            keys.append({"key":key,"value" : fuzz.token_set_ratio(item, key)})
        return self._db[max(keys,key=lambda x : x['value'])["key"]]
    def get_multiple(self,item, threshold = 75):
        keys = []
        to_return = []
        for key in self._db:
            keys.append({"key":key,"value" : fuzz.token_set_ratio(item, key)})
        for key in keys:
            if key["value"] > threshold:
                for db_item in self._db[key["key"]]:
                    to_return.append(db_item)
        return to_return
    def __getitem__(self, item):
        keys = []
        for key in self._db:
            keys.append({"key":key,"value" : fuzz.token_set_ratio(item, key)})
        return self._db[max(keys,key=lambda x : x['value'])["key"]]
    def __len__(self):
        return len(self._db)
    def all(self):
        return self._db
