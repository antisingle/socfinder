from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Date, Float, Text, Numeric
from sqlalchemy.types import JSON
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    # Основные поля (1-4)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contest = Column(String)
    year = Column(Integer, index=True)
    direction = Column(String, index=True)
    
    # Даты и регион (5-6)
    date_req = Column(Date)
    region = Column(String, index=True)
    
    # Организация (7-9)
    org = Column(String, index=True)
    inn = Column(String)
    ogrn = Column(String)
    
    # Даты реализации (10-11)
    implem_start = Column(Date)
    implem_end = Column(Date)
    
    # Статус и рейтинг (12-13)
    winner = Column(Boolean, index=True)
    rate = Column(Float)
    
    # Финансы (14-16)
    money_req_grant = Column(Numeric)
    cofunding = Column(Numeric)
    total_money = Column(Numeric)
    
    # Описание проекта (17-22)
    description = Column(Text)
    goal = Column(Text)
    tasks = Column(Text)
    soc_signif = Column(Text)
    pj_geo = Column(Text)
    target_groups = Column(Text)
    
    # Контакты и ссылки (23-26)
    address = Column(Text)
    web_site = Column(String)
    req_num = Column(String)
    link = Column(String)
    
    # Географические коды (27-29)
    okato = Column(String)
    oktmo = Column(String)
    level = Column(String)
    
    # Дополнительные поля
    coordinates = Column(JSON)  # {lat, lng} - вычисляемое поле


