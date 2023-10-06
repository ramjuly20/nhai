from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

Base = declarative_base()

engine = create_engine('mysql+mysqlconnector://root:ram@localhost:3306/nhai')
Session = sessionmaker(bind=engine)
session_db = Session()


class User(Base):
    __tablename__ = 'users'  # Corrected table name
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )
    # Define a one-to-many relationship with UserSession
    sessions = relationship("UserSession", back_populates="user")

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

class UserSession(Base):
    __tablename__ = 'user_sessions'  # Use a different name for the table
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'),  nullable=False)  # Foreign key to the users table
    token = Column(String(255), unique=True, nullable=False)  # Unique session token
    login_time = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    logout_time = Column(TIMESTAMP, default=None, nullable=True)
    user = relationship('User', back_populates='sessions')

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token


Base.metadata.create_all(engine)