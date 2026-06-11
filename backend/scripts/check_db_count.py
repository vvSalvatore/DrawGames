from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
db = client['drawgames']
print('games_count', db.games.count_documents({}))
print('sample', list(db.games.find({}, {'steam_app_id':1, 'title':1}).limit(5)))
