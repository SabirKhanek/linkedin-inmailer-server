import json
from common.exceptions import BadRequestException, InvalidCredentialsException, NotFoundExcetion
from db import Session, engine, select
from db.models.user import User
from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError

class UserService():
    def _get_user_by_username(self, username: str) -> User:
        with Session(engine) as session:
            statement = select(User).where(User.username==username).limit(1)
            result = session.exec(statement)
            user = result.one_or_none()
            if not user:
                raise NotFoundExcetion(f"User with {username} not found")
            return user
    
    def get_user_by_username(self, username: str):
        user = self._get_user_by_username(username)
        return self._exclude_privates(user)
    
    def add_user(self, username: str, password: str):
        user = User(username=username,password=bcrypt.hash(password))

        with Session(engine) as session:
            session.add(user)

            try:
                session.commit()
                user.username
            except IntegrityError as e:
                raise BadRequestException(f"User with {username} already exists") from e
        return self._exclude_privates(user)
    
    def validate_user_credentials(self, username: str, password: str):
        user = self._get_user_by_username(username)
        
        if user is None or not bcrypt.verify(password, user.password):
            raise InvalidCredentialsException("Invalid username or password")
        
        return self._exclude_privates(user)

    def _exclude_privates(self, user: User):
        return user.model_dump(exclude=["password"])
    
    def add_user_cookies(self, username: str, cookies: dict):
        user = self._get_user_by_username(username)

        with Session(engine) as session:
            user.cookie = cookies

            session.add(user)
            session.commit()
            user.username

        return self._exclude_privates(user)

