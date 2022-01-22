from db_conn import engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DECIMAL, Date, ForeignKey, cast, func, extract
from sqlalchemy.orm import sessionmaker, column_property, relationship

Base = declarative_base()

class Bourbon(Base):
    __tablename__ = 'bourbon'

    id = Column(Integer, primary_key=True)
    productid = Column(String)
    storeid = Column(String)
    quantity = Column(Integer)
    distance = Column(DECIMAL)
    latitude = Column(DECIMAL)
    longitude = Column(DECIMAL)
    area_code = Column(String)
    prefix = Column(String)
    linenumber = Column(String)
    phone_number = Column(String)
    insert_dt = Column(Date)
    insert_date = column_property(cast(insert_dt, Date))
    year = column_property(extract('year', insert_dt))

    products = relationship("Bourbon_desc")
    stores = relationship("Bourbon_stores")


class Bourbon_desc(Base):
    __tablename__ = 'bourbon_desc'

    productid = Column(String, ForeignKey('bourbon.productid'), primary_key=True)
    description = Column(String)
    size = Column(String)
    age = Column(String)
    proof = Column(DECIMAL)
    price = Column(DECIMAL)


class Bourbon_stores(Base):
    __tablename__ = 'bourbon_stores'

    storeid = Column(String, ForeignKey('bourbon.storeid'), primary_key=True)
    store_full_addr = Column(String)
    store_addr_1 = Column(String)
    store_addr_2 = Column(String)
    store_addr_3 = Column(String)
    store_city = Column(String)
    store_state = Column(String)
    store_zip = Column(String)


class ETL_control_status(Base):
    __tablename__ = 'etl_control_status'

    load_status = Column(String, primary_key=True)
    load_date = Column(Date)


Session = sessionmaker(bind=engine)
session = Session()

product_list_q = session.query(Bourbon_desc.productid, Bourbon_desc.description) \
                        .order_by(Bourbon_desc.description)

store_list_q = session.query(
                        Bourbon_stores.storeid, 
                        func.Concat(Bourbon_stores.store_addr_2, ' ', Bourbon_stores.store_city).label('store_addr_disp')) \
                        .order_by(Bourbon_stores.storeid)