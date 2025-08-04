from pymongo import MongoClient
from config.configs import MONGO_URL

class MongoPool:
    _instances = {}

    def __new__(cls, collection_name):
        if collection_name not in cls._instances:
            cls._instances = super().__new__(cls)
            cls._instances.client = MongoClient(
                MONGO_URL
            )
            cls._instances.db = cls._instances.client["gaokao"]
            cls._instances.collection = cls._instances.db[collection_name]
        return cls._instances

    @classmethod
    def get_collection(cls, name):
        return cls.db[name]

    @classmethod
    def close(cls):
        cls.client.close()
