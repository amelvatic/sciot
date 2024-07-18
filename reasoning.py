import gateway
from multiprocessing.connection import Client
import os
import re
import subprocess
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

class Reasoner():
     def __init__(self, planner_timeout=10):
          #super(Reasoner, self).__init__()
          self.input_data = {}
          self.planner_timeout = planner_timeout

     def contextualize_input_data(self):

          water_level_threshold = 20
          too_cold_threshold = 20
          too_warm_threshold = 30
          too_dark_threshold = 30
          too_bright_threshold = 101
          soil_hum_threshold = 20
          
          too_little_airhum_threshold = 30
          too_much_airhum_threshold = 90

          if 'plant' in self.input_data:
               plant_data = self.input_data['plant'].split(";")
               if(len(plant_data)>=2):
                    plant_data = plant_data[1].split(',')
                    if(len(plant_data)>=9):

                         too_cold_threshold = float(plant_data[4])
                         too_warm_threshold = float(plant_data[5])

                         too_dark_threshold = float(plant_data[2])
                         too_bright_threshold = float(plant_data[3])
     
                         soil_hum_threshold = float(plant_data[6])

                         too_little_airhum_threshold = float(plant_data[7])
                         too_much_airhum_threshold = float(plant_data[8])

          context = []

          if ((type(self.input_data) != dict) or (not self.input_data)):
               return None

          if 'water_level' in self.input_data:
               try:
                    values = []
                    for reading in self.input_data['water_level']:
                         if(reading!=''):
                              v = reading.strip().split(',')[1]
                              values += [float(v)]

                    most_common_value = float(max(set(values), key=values.count))
                    if most_common_value >= water_level_threshold:
                         context += ["tank-full s"]
               except Exception as e:
                    print("Wrong data format: water_level: " + str(e))
          if 'act_states' in self.input_data:
               try:
                    values = []
                    for reading in self.input_data['act_states']:
                         v = reading.strip().split(',[')[1]
                         v = v[:-1]
                         vs = v.split(',')
                         res = []
                         for x in vs:
                              res += [x]
                         values += [res]

                    latest_value = values[len(values)-1]
               
                    if latest_value[0].strip() == "True":
                         context += ["lid-open s"]
                    if latest_value[1].strip() == "True":
                         context += ["lamp-on s"]
                    if latest_value[2].strip() == "True":
                         context += ["refill-indicator-light-on s"]
                    if latest_value[3].strip() == "True":
                         context += ["fan-on s"]
               except Exception as e:
                    print("Wrong data format: act_states: " + str(e))
          if 'soil_humidity' in self.input_data:
               try:
                    values = []
                    for reading in self.input_data['soil_humidity']:
                         v = reading.strip().split(',')[1]
                         values += [float(v)]

                    latest_value = float(values[len(values)-1])

                    if latest_value < soil_hum_threshold:
                         context += ["low-soil-hum s"]
               except Exception as e:
                    print("Wrong data format: soil_humidity: " + str(e))
          if 'light' in self.input_data:
               try:
                    values = []
                    for reading in self.input_data['light']:
                         v = reading.strip().split(',')[1]
                         values += [float(v)]

                    latest_value = float(values[len(values)-1])

                    print("light level: "+ str(latest_value))
                    if latest_value <= too_dark_threshold:
                         context += ["too-dark s"]
                    elif latest_value >= too_bright_threshold:
                         context += ["too-bright s"]
               except Exception as e:
                    print("Wrong data format: light: " + str(e))
          if 'air_t&h' in self.input_data:
               try:
                    values = []
                    for reading in self.input_data['air_t&h']:
                         v = reading.strip().split(',[')[1]
                         v = v[:-1]
                         vs = v.split(',')
                         res = []
                         for x in vs:
                              res += [float(x)]
                         values += [res]

                    latest_value = values[len(values)-1]

                    if latest_value[0] <= too_cold_threshold:
                         context += ["too-cold s"]
                    elif latest_value[0] >= too_warm_threshold:
                         context += ["too-warm s"]
                    if latest_value[1] <= too_little_airhum_threshold:
                         context += ["too-litlle-hum s"]
                    elif latest_value[1] >= too_much_airhum_threshold:
                         context += ["too-much-hum s"]
               except Exception as e:
                    print("Wrong data format: air_t&h: " + str(e))
     
          if 'weather' in self.input_data:
               try:
                    values = []
                    for reading in self.input_data['weather']:
                         v = reading.strip().split(',[')[1]
                         v = v[:-1]
                         vs = v.split(',')
                         res = []
                         for x in vs:
                              res += [x.strip()]
                         values += [res]

                    latest_value = values[len(values)-1]

                    if latest_value[0] == "false":
                         context += ["raining w"]
               except Exception as e:
                    pass

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
                 (and(or(tank-full s) (refill-indicator-light-on s))(not(and(refill-indicator-light-on s)(tank-full s))))

                 (and(or(not(too-dark s))(lamp-on s))(not(and(not(too-dark s))(lamp-on s))))
                 (and(or(not(too-warm s))(fan-on s))(not(and(not(too-warm s))(fan-on s))))
                 (and(or(not(too-much-hum s))(lid-open s))(not(and(not(too-much-hum s))(lid-open s))))
                 (or(not(tank-full s))(not(low-soil-hum s)))
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

     def invoke_planner(self, domfile, probfile, planner):
          #/home/amel/sciot/FF-v2.3/./ff -o /home/amel/dev/sciot/garden_domain.pddl -f /home/amel/dev/sciot/garden_problem.pddl
          result = subprocess.run([planner, '-o', domfile, '-f', probfile], stdout=subprocess.PIPE)
          resultstring = result.stdout.decode('utf-8')
          print(resultstring)

          if resultstring=="":
               print("Something went wrong executing the planner")
               return []

          actions_to_execute = []
          valid_plan = -1
          for item in resultstring.split("\n"):
               if "found legal plan as follows" in item:
                   valid_plan = 0
               elif "goal can be simplified to TRUE. The empty plan solves it" in item:
                    print('Goal is already satisfied.')
                    return actions_to_execute
               elif "goal can be simplified to FALSE. No plan will solve it" in item:
                    print('Goal is not reachable.')
                    return []

          if (valid_plan == 0):
               plan_section = False
               for line in resultstring.split("\n"):
                    if not plan_section:
                         if re.match("step[\s]*[0]:\s", line):
                              plan_section = True
                              x = re.sub("step[\s]*[0-9]+:\s", "", line)
                              actions_to_execute += [x]
                    else:
                         if re.sub("[\s]*", "", line) == "":
                              plan_section = False
                         else:
                              x = re.sub("[\s]*[0-9]+:\s", "", line)
                              actions_to_execute += [x]

          return actions_to_execute

     def contextualize_planner_actions(self, planner_actions):
          out_actions = []
          if(type(planner_actions) == list):
               for action in planner_actions:
                    out_actions += [action.split(" ")[0]]
          return out_actions

     def execute_actions(self, list_of_actions):
          for item in list_of_actions:
               if (item == "WATER_PLANT"):
                    gateway.water_pump_on()
               elif (item == "TURN_ON_LIGHT"):
                    gateway.light(True)
               elif (item == "TURN_OFF_LIGHT"):
                    gateway.light(False)
               elif (item == "TURN_ON_FAN"):
                    gateway.fan(True)
               elif (item == "TURN_OFF_FAN"):
                    gateway.fan(False)
               elif (item == "REFILL_TANK_LIGHT_ON"):
                    gateway.indicator_led(True)
               elif (item == "REFILL_TANK_LIGHT_OFF"):
                    gateway.indicator_led(False)
               elif (item == "OPEN_LID"):
                    gateway.servo(True)
               elif (item == "CLOSE_LID"):
                    gateway.servo(False)

     def get_fresh_input_data(self):
          dbms_address = ('localhost', 6000)
          
          request_timeout = 30
          no_data_blocks = 1
          no_data_blocks_water_level = 3

          while True:
               try:
                    with Client(dbms_address, authkey=b'pw') as conn:
                         conn.send(["get", "all", no_data_blocks])
                         response = conn.recv()
                         #print(response)
                         if not '404' in response:
                              self.input_data = response
                    time.sleep(2)
                    with Client(dbms_address, authkey=b'pw') as conn:
                         conn.send(["get", "water_level", no_data_blocks_water_level])
                         response = conn.recv()
                         #print(response)
                         if not '404' in response:
                              if 'water_level' in response:
                                   self.input_data['water_level'] = response['water_level']
                    time.sleep(2)
                    with Client(dbms_address, authkey=b'pw') as conn:
                         conn.send(["get", "plant"])
                         response = conn.recv()
                         #print(response)
                         if not '404' in response:
                              if 'plant' in response:
                                   self.input_data['plant'] = response['plant']
               except Exception as e:
                    print(e)
               time.sleep(request_timeout)

     def planning(self):
          while True:
               if not gateway.manual_control:
                    init_planner_states = self.contextualize_input_data()

                    if init_planner_states == None:
                         continue

                    probfile = self.create_probfile(init_planner_states)
     
                    #old_probfile = '/home/amel/dev/sciot/garden_problem.pddl'
                    
                    on_pi = True
                    if(on_pi):
                         pi_planner = '/home/pi/Downloads/FF-v2.3/./ff'
                         pi_domfile = '/home/pi/iot/garden_domain.pddl'
                         planner_actions = self.invoke_planner(pi_domfile, probfile, pi_planner)
                    else:
                         planner = '/home/amel/sciot/FF-v2.3/./ff'
                         domfile = '/home/amel/dev/sciot2/sciot/garden_domain.pddl'
                         planner_actions = self.invoke_planner(domfile, probfile, planner)
     
                    actions = []
                    if planner_actions != None:
                         print("Planner actions: " + str(planner_actions))
                         actions = self.contextualize_planner_actions(planner_actions)

                    self.execute_actions(actions)

               time.sleep(self.planner_timeout)

     def start(self):
          t1 = threading.Thread(target=self.get_fresh_input_data)
          t1.start()

          t2 = threading.Thread(target=self.planning)
          t2.start()
