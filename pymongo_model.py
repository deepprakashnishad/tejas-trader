import pymongo
from utils import my_constants as mconst


mongoclient = pymongo.MongoClient(mconst.DB_SERVER_URL)


class PyMongoConnectionSingleton:

    __instance = None

    @staticmethod
    def getInstance(host, port, db_name):
        if PyMongoConnectionSingleton.__instance is None:
            PyMongoConnectionSingleton.__instance = PyMongoConnectionSingleton(host, port, db_name)
        return PyMongoConnectionSingleton.__instance

    def __init__(self, host, port, db_name):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[db_name]


class PymongoDocument:

    def __init__(self, pmc):
        self.collection_name = self.__class__.__name__
        self.col = pmc.db[self.collection_name]
        print(self.collection_name)

    def find_all(self):
        results = self.col.find()
        print(results)

