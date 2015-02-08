from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import requests, json


Base = automap_base()

# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine('mssql+pyodbc://devel:n3wmediam3d@NEIL-DESKTOP/FRESH?driver=SQL Server; Trusted_Connection=Yes', echo=True)

# reflect the tables
Base.prepare(engine, reflect=True)

# mapped classes are now created with names by default
# matching that of the table name.

session = Session(engine)

github_url = "https://nkellis.herokuapp.com/api/v1.0/posts"
headers = {'content-type': 'application/json'}

Item = Base.classes.Item
for instance in session.query(Item).order_by(Item.ID): 
    print instance.Description
    data = json.dumps({'productName':instance.Description})
    r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))


print r.json