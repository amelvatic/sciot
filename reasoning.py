from array import array
import gateway
from multiprocessing import Process
from multiprocessing.connection import Client
import subprocess
import os
import re
import threading
import time

#from signal import signal, SIGPIPE, SIG_DFL  
#signal(SIGPIPE,SIG_DFL)

'''class FreshDataRequester(Process):
     def __init__(self, reasoner):
        super(FreshDataRequester, self).__init__()
        self.reasoner = reasoner
    
     def run(self):
          dbms_address = ('localhost', 6000)
          
          no_data_blocks = 1
          while True:
               with Client(dbms_address, authkey=b'pw') as conn:
                    conn.send(["get", no_data_blocks])
                    response = conn.recv()
                    #print(response)
                    self.reasoner.set_input_data(response)
               time.sleep(5)'''

class Reasoner(Process):
     def __init__(self, out_queue, gateway, planner_timeout=5):
          super(Reasoner, self).__init__()
          self.input_data = []
          self.gateway = gateway
          self.out_queue = out_queue
          self.planner_timeout = planner_timeout

     def contextualize_input_data(self, input_data):
          a = False

          context = []

          if "abc" in self.input_data:
               context += ["tank-full s"]
          if a:
               context += ["refill-indicator-light-on s"]
          if a:
               context += ["lamp-on s"]
          if a:
               context += ["low-soil-hum s"]
          if a:
               context += ["too-bright s"]
          if a:
               context += ["too-dark s"]
          if a:
               context += ["too-warm s"]
          if a:
               context += ["too-cold s"]
          if a:
               context += ["lid-open s"]
          if a:
               context += ["fan-on s"]
          if a:
               context += ["raining w"]

          return context

     def create_probfile(self, init_planner_states):
          head = '''(define
               (problem gardenproblem)
               (:domain garden)
               (:objects 
                    s - state
                    w - world
               )
               (:init 
                    (dummy1 s)'''

          initstates = ''
          for state in init_planner_states:
               initstates += '(' + state +')\n'

          tail = ''')
               (:goal (and
                 (and(or (tank-full s) (refill-indicator-light-on s))(not(and(refill-indicator-light-on s)(tank-full s))))
                 (not(too-bright s))
                 (not(too-dark s))
                 (not(too-cold s))
                 (not(too-warm s))
                 (not (low-soil-hum s))
                 (not(and(raining w)(lid-open s)))
               )
               )
               )'''

          filename = 'p.pddl'
          with open(filename, 'w+') as file:
               file.write(head)
               file.write(initstates)
               file.write(tail)
               file.write('\n')

          cwd = os.getcwd()
          return cwd + '/' + filename

     def invoke_planner(self, domfile, probfile, planner='/home/amel/sciot/FF-v2.3/./ff'):
          #/home/amel/sciot/FF-v2.3/./ff -o /home/amel/dev/sciot/garden_domain.pddl -f /home/amel/dev/sciot/garden_problem.pddl
          result = subprocess.run([planner, '-o', domfile, '-f', probfile], stdout=subprocess.PIPE)
          resultstring = result.stdout.decode('utf-8')
          #print(resultstring)

          if resultstring=="":
               print("Something went wrong executing the planner")
               return None

          actions_to_execute = []
          b = -1
          for item in resultstring.split("\n"):
               if "found legal plan as follows" in item:
                   b = 0
               elif "goal can be simplified to TRUE. The empty plan solves it" in item:
                    return actions_to_execute
               elif "goal can be simplified to FALSE. No plan will solve it" in item:
                    return None

          # problem step 0 matches this pattern: we need the collect all lines following 'step 0...'
          if (b == 0):
               for line in resultstring.split("\n"):
                    if  re.match("step[\s]*[0]:\s", line):
                         x = re.sub("step[\s]*[0-9]+:\s", "", line)
                         actions_to_execute += [x]

          return actions_to_execute

     def contextualize_planner_actions(self, planner_actions):
          out_actions = []
          for action in planner_actions:
               out_actions += [action.split(" ")[0]]
          return out_actions

     def execute_actions(self, list_of_actions):
          for item in list_of_actions:
               if (item == "WATER_PLANT"):
                    self.gateway.water_pump()
               elif (item == "TURN_ON_LIGHT"):
                    self.gateway.light(True)
               elif (item == "TURN_OFF_LIGHT"):
                    self.gateway.light(False)
               elif (item == "TURN_ON_FAN"):
                    self.gateway.fan(True)
               elif (item == "TURN_OFF_FAN"):
                    self.gateway.fan(False)
               elif (item == "REFILL_TANK_LIGHT_ON"):
                    self.gateway.tank_light(True)
               elif (item == "REFILL_TANK_LIGHT_OFF"):
                    self.gateway.tank_light(False)
               elif (item == "OPEN_LID"):
                    self.gateway.open_lid(True)
               elif (item == "CLOSE_LID"):
                    self.gateway.open_lid(False)

     def get_fresh_input_data(self):
          dbms_address = ('localhost', 6000)
          
          no_data_blocks = 1
          while True:
               with Client(dbms_address, authkey=b'pw') as conn:
                    conn.send(["get", no_data_blocks])
                    response = conn.recv()
                    self.input_data = response
               time.sleep(5)

     def run(self):
          t1 = threading.Thread(target=self.get_fresh_input_data)
          t1.start()

          while True:
               init_planner_states = self.contextualize_input_data(self.input_data)
               probfile = self.create_probfile(init_planner_states)

               #old_probfile = '/home/amel/dev/sciot/garden_problem.pddl'
               planner = '/home/amel/sciot/FF-v2.3/./ff'
               planner_actions = self.invoke_planner('/home/amel/dev/sciot/garden_domain.pddl', probfile, planner)

               if planner_actions != None:
                    print(planner_actions)

               actions = self.contextualize_planner_actions(planner_actions)
               self.execute_actions(actions)
               self.out_queue.put(actions)

               time.sleep(self.planner_timeout)
