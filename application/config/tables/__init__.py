from .dwh_mssql import BINDS as DWH_MSSQL_BINDS
from .dwh_postgres import BINDS as DWH_POSTGRES_BINDS
from .navision import BINDS as NAV_BINDS
from sqlalchemy.orm import sessionmaker


Session = sessionmaker(binds={
    **DWH_POSTGRES_BINDS,
    **DWH_MSSQL_BINDS,
    **NAV_BINDS,
})
# Session = sessionmaker()
# Session.configure(binds={
#     **DWH_POSTGRES_BINDS,
#     **DWH_MSSQL_BINDS,
#     **NAV_BINDS,
# })
session = Session()
