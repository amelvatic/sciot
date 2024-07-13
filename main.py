import dbms
import gateway

import reasoning
import dbms
import time
          
db = dbms.DBMS()
db.start()

reasoner = reasoning.Reasoner()
reasoner.start()
