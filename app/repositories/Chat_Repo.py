from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from typing import Optional, List, Tuple
from loguru import logger

from app.repositories.Base_repo import BaseRepository
from app.models.Chat import ChatRoom, ChatMessage


class ChatRepository(BaseRepository[ChatRoom]):

    def __init__(self, db: Session):
        super().__init__(ChatRoom, db)
        
    # Get room  by application id 
    
    def room_by_application(self , application_id : str) -> Optional[ChatRoom]:
        
        # Get room linked to job application 
        
        result = self._db.execute(select(ChatRoom).where(ChatRoom.application_id == application_id))
        
        return result.scalar_one_or_none()
    
    # Get room with chatmessage 
    
    def get_room_by__with_message(self , room_id : int) -> Optional[ChatRoom]:
        
        # Get chat room + all message 
        
        result = self._db.execute(select(ChatRoom).options(joinedload(ChatRoom.messages)).where(ChatRoom.id == room_id))
        
        return result.scalar_one_or_none()
    
    
    # Get room by worker 
    
    def get_room_by_worker(self , worker_id : int , offset : int , limit : int = 20) -> Tuple[List[ChatRoom] , int]:
        
        # all chat room for worker  , one worker connected with many employers so it loads all converstaion 
        
        base_query = (select(ChatRoom).where(ChatRoom.worker_id == worker_id,
                                             ChatRoom.is_active == True))
        
        count_query = (select(func.count(ChatRoom.id)).where(ChatRoom.worker_id == worker_id , 
                                                       ChatRoom.is_active == True))
        
        result = self._db.execute(base_query.order_by(ChatRoom.created_at.desc()).offset(offset).limit(limit))
        
        count  = self._db.execute(count_query)
        
        return list(result.scalars().all() , count.scalar_one())
        
        
    # Get room by employer
    
    def get_room_by_employer(self , employer_id : int , offset : int , limit : int = 20) -> Tuple[List[ChatRoom] , int]:
        
        # all chat room for worker  , one worker connected with many employers so it loads all converstaion 
        
        base_query = (select(ChatRoom).where(ChatRoom.worker_id == employer_id,
                                             ChatRoom.is_active == True))
        
        count_query = (select(func.count(ChatRoom.id)).where(ChatRoom.worker_id == employer_id, 
                                                       ChatRoom.is_active == True))
        
        result = self._db.execute(base_query.order_by(ChatRoom.created_at.desc()).offset(offset).limit(limit))
        
        count  = self._db.execute(count_query)
        
        return list(result.scalars().all() , count.scalar_one())
            
    #Create Room 
    
    def create_room(self , application_id : int  , worker_id : int , employer_id : int) -> ChatRoom:
        
        # create a new room after worker is hired 
        
        room = ChatRoom(application_id = application_id ,
                        worker_id = worker_id,
                        employer_id = employer_id ,
                        is_active = True)
        
        self._db.add(room)
        self._db.flush()
        self._db.refresh(room)
        logger.info(
            f"Chat room created | application_id={application_id} "
            f"worker_id={worker_id} employer_id={employer_id}"
        )
        return room
    
    # close room 
    
    def close_room(self , room_id : int ) -> None:
        
        self.update(room_id, is_active = False)
        
        logger.info(f"Chat room closed | room_id={room_id}")
        
    # Check if user if the worker in this room 
    
    def is_participant(self , room_id : int , user_id : int) -> bool:          
        
        # check is user is a participant in room 
        
        from app.models.Worker import Worker
        from app.models.Employer import Employer
        
        # check if user is the worker in this room 
        
        worker_result = self._db.execute(
        select(ChatRoom)
       .join(Worker, Worker.id == ChatRoom.worker_id)
       .where(ChatRoom.id == room_id)
       .where(Worker.user_id == user_id) 
         )
        
        if worker_result.scalar_one_or_none():
            return True
        
        
        # Check if user is the employer in this room
        employer_result = self._db.execute(
            select(ChatRoom)
            .join(Employer, Employer.id == ChatRoom.employer_id)
            .where(ChatRoom.id == room_id)
            .where(Employer.user_id == user_id)
        )
        return employer_result.scalar_one_or_none() is not None

    def get_messages(
        self,
        room_id: int,
        offset: int = 0,
        limit: int = 50,
                                 ) -> Tuple[List[ChatMessage], int]:
        # Returns paginated messages for a room, oldest first
       
        base_query = (
            select(ChatMessage)
            .where(ChatMessage.room_id == room_id)
        )
        count_query = (
            select(func.count(ChatMessage.id))
            .where(ChatMessage.room_id == room_id)
        )

        result = self._db.execute(
            base_query
            .order_by(ChatMessage.created_at.asc())   # oldest first for chat
            .offset(offset)
            .limit(limit)
        )
        count = self._db.execute(count_query)

        return list(result.scalars().all()), count.scalar_one()    
    
        
    
    def create_message(
        self,
        room_id: int,
        sender_id: int,
        content: str,
                          ) -> ChatMessage:
        message = ChatMessage(
            room_id=room_id,
            sender_id=sender_id,
            content=content,
            is_read=False,
        )
        self._db.add(message)
        self._db.flush()
        self._db.refresh(message)
        logger.debug(f"Message created | room_id={room_id} sender_id={sender_id}")
        return message

    def mark_messages_read(self, room_id: int, reader_id: int) -> int:
        
        #Mark all unread messages as read except sender's own messages
        
        from sqlalchemy import update
        result = self._db.execute(
            update(ChatMessage)
            .where(
                and_(
                    ChatMessage.room_id == room_id,
                    ChatMessage.sender_id != reader_id,
                    ChatMessage.is_read == False,
                )
            )
            .values(is_read=True)
        )
        
        self._db.flush()
        logger.debug(
            f"Messages marked read | room_id={room_id} "
            f"reader_id={reader_id} count={result.rowcount}"
        )
        return result.rowcount
    
    
    def get_unread_count(self, room_id: int, user_id: int) -> int:
        
        # Count unread messages for a user in a room"""
        
        result = self._db.execute(
            select(func.count(ChatMessage.id))
            .where(ChatMessage.room_id == room_id)
            .where(ChatMessage.sender_id != user_id)
            .where(ChatMessage.is_read == False)
        )
        return result.scalar_one()