from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

dbuser = config.get('ri', 'dbuser')

dbhost = config.get('ri', 'dbhost')
dbname = config.get('ri', 'dbname')



# Replace 'hostname', 'port', and 'database_name' with your MySQL server details
DATABASE_URL = 'mysql+pymysql://' + dbuser + '@' + dbhost + '/' + dbname

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Define metadata
metadata = MetaData()

sim=Table('sim', metadata,autoload_with=engine)
phone_number=input("Enter Phone Number :")

with engine.connect() as connection:
    # Inserting a single row
    connection.execute(sim.insert(), {'phone_number':phone_number  })

    # Inserting multiple rows
    connection.commit()
print(phone_number)

# Close the connection
engine.dispose()
