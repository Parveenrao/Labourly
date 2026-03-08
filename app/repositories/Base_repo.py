from sqlalchemy.orm import Session
from typing import Optional , Generic , List , Dict , TypeVar , Tuple , Type , Any
from sqlalchemy import select , update , delete , func , asc , desc 
from loguru import logger
from pydantic import BaseModel

T = TypeVar("T")

class BaseRepository(Generic[T]):
    
    """Generic repo --> Every repo inherit from it 
      
       Provide full CRUD + pagination + sorting + bulk_ops"""
       
    def __init__(self , model : Type[T] , db : Session):
        self._model = model 
        self._db = db
        
    # Create 
    
    def Create(self , **kwargs) -> T:
        instance = self._model(**kwargs)
        self._db.add(instance)
        self._db.flush()           # -> flush insert into db , but not commit ,  id are auto generated          
        self._db.refresh(instance)  # Reload generatd fields like id
        
        logger.debug(f" Created {self._model.__name__} , id = {getattr(instance , id, None)}")
        
        return instance
    
    # Bulk - Create
    
    def bulk_create(self , schemas : List[BaseModel]) -> List[T]:
        if not schemas:
            return []
        
        instances = [self._model(**schema.model_dump(exclude = "id"))
                     
                     for schema in schemas]
        
        self._db.add_all(instances)
        
        self._db.flush()
        
        logger.debug(f" Bulk Created {len(instances)} {self._model__name__}")
        
        return instances
    
    # Read Single 
    
    def get_by_id(self , obj_id : Any) -> Optional[T]:
        
        return self._db.get(self._model , obj_id)             # we dont use here query because it build query first , so get() look identity map first
    
    
    # Read by other column
    
    def get_by_field(self , column , value) -> Optional[T]:
        
        if column.class_ not in self._model:
            raise ValueError("Columns does not belong to this model ") 
        
        result = self._db.execute(select(self._model).where(column = value))
        
        return result.scalar_one_or_none()
    
    # Real all 
    
    def get_all(self, offset : int = 0 , limit : int = 20 , order_by : str = "id" , order_dir :str = "desc") -> List[T]:
        
        MAX_LIMIT = 100
        limit = min(limit , MAX_LIMIT)
        
        column = getattr(self._model , order_by , None)
        
        if not column:
            raise ValueError(f"Invalid order_by field : {order_by}")
        
        if order_dir not in ["asc" , "desc"]:
            raise ValueError("order_dir must be 'asc' or 'desc' ")
        
        order = desc(column) if order_dir == "desc" else asc(column)
        
        stmt = (select(self._model).order_by(order).offset(offset).limit(limit))
        
        result = self._db.execute(stmt)
        
        return result.scalars().all()
    
    
    def get_many_by_field(self, field : str  , value , offset :int = 0 , limit : int = 20,
                          order_by :str  ="created_at" , order_dir : str = "desc") -> List[T]:
        
        column = getattr(self._model , field)
        
        order_col = getattr(self._model , order_by , self._model.id)
        
        order = desc(order_col) if order_by =="desc" else asc(order_col)
        
        stmt = (select(self._model).where(column == value).order_by(order).offset(offset).limit(limit))
        
        result = self._db.execute(stmt)
        
        return list(result.scalars().all())
        
        
    def get_by_many_ids(self, ids : List[int]) -> List[T]:
        
        if not ids:
            return []
        
        result = self._db.execute(select(self.mode).where(self._model.id.in_(ids)))
        
        return list(result.scalars().all())   
    
    def update(self, id : int , **kwargs) -> Optional[T]:
        
        # update fields by id 
        
        self._db.execute(update(self._model).where(self._model.id == id).values(**kwargs))
        
        
        self._db.flush()
        
        updated = self.get_by_id(id)
        
        
        logger.debug(f"Updated : {self._model.__name__} , id : {id} , fields = {list(kwargs.keys())}")
        
        return updated
    
    def update_by_fields(self, field : str , value , **kwargs) -> int:
        
        # Update rows by any field
        
        if not hasattr(self._model , field):
            raise ValueError(f"{field} is not a valid column")
        
        column = getattr(self._model , field)
        
        result = self._db.execute(update(self._model).where(column == value).values(**kwargs))
        
        self._db.flush()
        
        logger.debug(
        f"Updated {self.model.__name__} where {field}={value}"
           )
        
        return result.rowcount
    
    
    def delete(self, id : int) -> bool:
        
        # Delete by ID
        
        result = self._db.execute(delete(self._model).where(self._model.id == id))
        
        return result.rowcount > 0
    
    def delete_by_field(self , field : str , value) -> int:
        
        if not hasattr(self._model , field):
            raise ValueError(f"{field} is not a valid column")
        
        column = getattr(self._model , field)
        
        result = self._db.execute(delete(self._model).where(column == value))
        
        logger.debug(f"Deleted L {self._model.__name__} where {field} = {value}")
        
        return result.rowcount
    
#----------------------------------- Exist & Count-----------------------

    def exist(self, field: str , value) -> bool:
        
        # Check if any row is exist by any field or not 
        
        # check if column already exist
        if not hasattr(self._model  , field):
            raise ValueError(f"{field} is not a valid column")
        
        column = getattr(self._model , field)
        
        result = self._db.execute(select(self._model.id).where(column == value))
        
        return result.scalar_one_or_none() is not None
    
    
    def check_by_id(self, id:int) -> bool:
        
        # check if row exist by id or not 
        
        result = self._db.execute(select(self._model.id).where(self._model.id == id))
        
        return result.scalar_one_or_none() is not None
    
    def count(self, field: str = None, value=None) -> int:
    
        # base query
        query = select(func.count(self._model.id))

        if field and value is not None:
           if not hasattr(self._model, field):
              raise ValueError(f"{field} is not a valid column")

        column = getattr(self._model, field)

        query = query.where(column == value)

        result = self._db.execute(query)

        return result.scalar_one()
    
    
    def get_paginated(
         self,
         offset: int = 0,
         limit: int = 20,
         field: str | None = None,
         value=None,
         order_by: str = "created_at",
         order_dir: str = "desc",
         ) -> Tuple[List[T], int]:
         
         """
         Fetch paginated records and total count.

         Returns:
          (items, total_count)
          """

         # validate sorting column
         if not hasattr(self._model, order_by):
            order_by = "id"

         order_column = getattr(self._model, order_by)
         order = desc(order_column) if order_dir == "desc" else asc(order_column)

         # base queries
         query = select(self._model)
         count_query = select(func.count()).select_from(self._model)

         # optional filter
         if field and value is not None:
             if not hasattr(self._model, field):
                 raise ValueError(f"{field} is not a valid column")

         filter_column = getattr(self._model, field)
         query = query.where(filter_column == value)
         count_query = count_query.where(filter_column == value)

         # fetch paginated items
         items_result = self._db.execute(
         query.order_by(order).offset(offset).limit(limit)
          )
         items = list(items_result.scalars().all())

         # fetch total count
         count_result = self._db.execute(count_query)
         total = count_result.scalar_one()

         return items, total
        
        
        
        