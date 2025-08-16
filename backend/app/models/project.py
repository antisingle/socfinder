from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, BigInteger
from sqlalchemy.types import JSON
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contest = Column(String)
    year = Column(Integer, index=True)
    direction = Column(String, index=True)
    date_req = Column(DateTime)
    region = Column(String, index=True)
    org = Column(String, index=True)
    inn = Column(String)
    ogrn = Column(String)
    implem_start = Column(DateTime)
    implem_end = Column(DateTime)
    winner = Column(Boolean, index=True)
    rate = Column(Float)
    money_req_grant = Column(BigInteger)  # Исправлено для больших чисел
    cofunding = Column(BigInteger)        # Исправлено для больших чисел  
    total_money = Column(BigInteger)      # Исправлено для больших чисел
    description = Column(Text)
    goal = Column(Text)
    tasks = Column(Text)
    soc_signif = Column(Text)
    pj_geo = Column(Text)
    target_groups = Column(Text)
    address = Column(Text)
    web_site = Column(String)
    req_num = Column(String)
    link = Column(String)
    okato = Column(String)
    oktmo = Column(String)
    level = Column(String)
    coordinates = Column(JSON)  # {lat, lng}


