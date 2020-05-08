
class Visualization:

    def __init__(self,DataMapper):
        self.DataMapper=DataMapper
    def find(self,query):
        return self.DataMapper.find(query)
    def insert(self,query):
        return self.MongoDI.insert(query)
    def getImage(self,hashKey):
        return self.DataMapper.getImage(hashKey)
