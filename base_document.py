from bson import ObjectId

from database import Database
import marshmallow

database = Database().get_db()

class BaseDocument:
  meta = {}
  
  @classmethod
  def get_collection(cls):
    collection_name = cls.meta.get("collection", None)
    
    if collection_name is None:
      raise Error("No collection name provided")
    return database[collection_name]
  
  @classmethod
  def validate_schema(cls, params):
    try:
      schema = cls.meta.get("schema")
      return schema().load(params)
    except marshmallow.exceptions.ValidationError as error:
      raise Exception(error)
      
  @classmethod
  def create(cls, **kwargs):
    doc = cls.validate_schema(kwargs)    
    result = cls.get_collection().insert_one(doc)
    return cls.get(id=result.inserted_id)
      
  @classmethod
  def get(cls, **kwargs):
    if "id" in kwargs:
      kwargs["_id"] = (
          ObjectId(kwargs.pop("id")) if type(kwargs["id"]) is str else kwargs.pop("id")
      )
    result = cls.get_collection().find_one(kwargs)
    schema = cls.meta.get("schema")
    return schema().load(result) 

  @classmethod
  def getMany(cls, **kwargs):
    if "id" in kwargs:
      kwargs["_id"] = (
          ObjectId(kwargs.pop("id")) if type(kwargs["id"]) is str else kwargs.pop("id")
      )
    result = cls.get_collection().find(kwargs)
    schema = cls.meta.get("schema")
    return schema(many=True).load(result) 
  
  @classmethod
  def update(cls, id, **kwargs):
    doc = cls.get(id=id)

    for key, val in kwargs.items():
      doc[key] = val

    del doc["_id"]
    updated_doc = cls.validate_schema(doc)

    result = cls.get_collection().update_one({"_id": ObjectId(id)}, {"$set": updated_doc})
    return cls.get(id=id) if result.acknowledged else None
      
  @classmethod
  def delete(cls, id):
    cls.get_collection().delete_one({"_id": ObjectId(id)})
      
  @classmethod
  def list(cls, **kwargs):
    if "ids" in kwargs:
      ids = [ObjectId(a_id) if type(a_id) is str else a_id for a_id in kwargs.pop("ids")]
      kwargs["_id"] = {"$in": ids}
    
    collection = cls.get_collection()
    res = cls.get_collection().find()
    schema = cls.meta.get("schema")
    data = schema(many=True).load(res)
    return data