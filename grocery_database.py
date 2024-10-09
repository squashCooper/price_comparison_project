#database that will hold prices and names of items

 
#modules 
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#database url 

user = 'root'
password = 'password'
host = '172.17.0.1'
port = 3306
database = 'grocery_database'
Base = declarative_base()


def connection():
   return create_engine(
        url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, database
        )
    )
#class that inherits from database 
 
class groceryInfo(Base):

#creating tablename 
    __tablename__ = 'product_information'
    id = Column(Integer, primary_key = True)

    item_name = Column(String(100), unique = True, nullable = False)
    item_price = Column(String(20), unique = True, nullable = False)
    item_store = Column(String(50), unique = True, nullable = False)



if __name__ == '__main__':
 
    try:
    
    #connecting and verifying connection to database 
        engine = connection()
        print(
            f"Connection to the {host} for user {user} created successfully.")
    except Exception as ex:
        print("Connection could not be made due to the following error: \n", ex)

    Base.metadata.create_all(engine)
    print("Tables created successfully.")

    #create a session factory

  
    try:
        SessionLocal = sessionmaker(bind = engine)

        print("Database has been set up successfully")

    except Exception as ex:
        print("Database setup failed")

    