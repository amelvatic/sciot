import dbms
import gateway
from queue import Queue
import reasoning
import dbms
          
q = Queue()
g = gateway.Gateway()

db = dbms.DBMS()
db.start()

reasoner = reasoning.Reasoner(q, g)
reasoner.start()
