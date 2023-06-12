
import safrs
import json
from pymysql import cursors, connect
import pymysql
import sqlite3
#import postresql TODO

db = safrs.DB  

class FreeSQL():
      
         
        def __init__(self,
             sqlExpression: str):
            """Initialize a FreeSQL expression

            Args:
                sqlExpression (str): the database expression
            """
            
            self.sqlExpression = sqlExpression
        
        def execute(self, request):  
            data = []
            
            # fixup sql 
            # open connection, cursor, execute , findAll() 
            args = request.args
            sql = self.fixup(args)
            try:
                print(f"FreeSQL SQL Expression={sql}")
                conn_str = db.engine.url
                conn = self.openConnection()
                if conn_str.drivername == 'sqlite':
                    cursor = conn.cursor()
                    cur = cursor.execute(sql)
                    results = [dict((cur.description[i][0], value)
                        for i, value in enumerate(row)) for row in cur.fetchall()]
                    cur.connection.close()
                else:
                    cur = conn.cursor(pymysql.cursors.DictCursor)
                    cursor = cur.execute(sql)
                    results = cur.fetchall()
                data = json.dumps(results, indent=4,default=str) #return Decimal() as str
              
            except Exception as ex:
                print(ex)
                return {'error':f"{ex}"}
                
            return data 
        
        def openConnection(self) -> any: #Connection
            # Use the safrs.DB, not db!
            conn_str = db.engine.url
            host = conn_str.host or "127.0.0.1"
            port = conn_str.port or "5656"
            user = conn_str.username
            pw = conn_str.password
            database = conn_str.database
            if conn_str.drivername == 'sqlite':
                return sqlite3.connect(database)
            elif conn_str.drivername == 'mysql+pymysql':
                return  pymysql.connect(
                    host=host,
                    port=port,
                    user=user,
                    passwd=pw,
                    db=database,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor)
            else:
                print(f"Connection database type {conn_str.drivername} not supported by FreeSQL")
                return None
            
        def fixup(self, *args):
            """
                LAC FreeSQL passes these args
                -- perhaps generate a function
                these were place holders that are passed by client or defaulted
                @{SCHEMA} 
                @{WHERE} 
                @{JOIN}
                @{ARGUMENT.} may include prefix (e.g. =main:entityName.attrName)
                @{ORDER}
                @{arg_attrname}
            """
            sql = self.sqlExpression
            if sql is not None:
                schema = ""
                whereStr = "1=1" #args.get("@where")
                joinStr = ""  #args.get("@join","")
                orderStr = "1" #args.get("@order","1")
            
                sql = sql.replace(":schema",schema, 10)
                sql = sql.replace(":where",whereStr, 10)
                sql = sql.replace(":order",orderStr, 10)
                sql = sql.replace(":join",joinStr, 10)
            return sql