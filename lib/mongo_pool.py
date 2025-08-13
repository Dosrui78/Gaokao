from pymongo import MongoClient
from config.configs import MONGO_URL

class MongoPool:
    _instances = {}

    def __new__(cls, collection_name):
        if collection_name not in cls._instances:
            instance = super().__new__(cls)
            instance.client = MongoClient(MONGO_URL)
            instance.db = instance.client["gaokao"]
            instance.collection = instance.db[collection_name]
            cls._instances[collection_name] = instance
        return cls._instances[collection_name]

    @classmethod
    def get_collection(cls, name):
        return cls.db[name]

    @classmethod
    def close(cls):
        cls.client.close()
