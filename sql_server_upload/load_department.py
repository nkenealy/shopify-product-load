from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import requests, json

Base = automap_base()

# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine('mssql+pyodbc://devel:n*************d@NEIL-DESKTOP/FRESH?driver=SQL Server; Trusted_Connection=Yes', echo=True)

# reflect the tables
Base.prepare(engine, reflect=True)

# mapped classes are now created with names by default
# matching that of the table name.

session = Session(engine)
headers = {'content-type': 'application/json'}

Department = Base.classes.Department
for instance in session.query(Department).order_by(Department.ID): 
    data = json.dumps({'title': instance.Name,\
                       'pos_dept_id': instance.ID })
    github_url = "https://nkellis.herokuapp.com/api/v1.0/custom_collections/"
    print data
    r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n*************d'))
    print r.json
    #Select SupplierName from supplier where Supplier.ID=instance.ID    
