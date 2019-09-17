from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random

class TerranAgent(base_agent.BaseAgent):  

  def __init__(self):
    super(TerranAgent, self).__init__()
    self.attack_coordinates = None
    self.scv_sent_to_harvest = False
    self.camera = False
    self.rally_units = False
    self.upgrade_combatshield = False
    self.upgrade_stimpack = False
    self.reactor_built=False
    self.attack_sent=False

  def can_do(self, obs, action):                                                    
    return action in obs.observation.available_actions

  def unit_type_is_selected(self, obs, unit_type):                                    #Check selection
    if (len(obs.observation.single_select) > 0 and
        obs.observation.single_select[0].unit_type == unit_type):
      return True
    
    if (len(obs.observation.multi_select) > 0 and
        obs.observation.multi_select[0].unit_type == unit_type):
      return True
    
    return False


  def get_units_by_type(self, obs, unit_type):
    return [unit for unit in obs.observation.feature_units
            if unit.unit_type == unit_type]


  def my_supply_depot(self, obs):
    supply_depot = self.get_units_by_type(obs, units.Terran.SupplyDepot)
    food_cap = obs.observation.player.food_cap

    if len(supply_depot) == 0 or food_cap < 40:
        if self.unit_type_is_selected(obs, units.Terran.SCV): 
          if self.can_do(obs,actions.FUNCTIONS.Build_SupplyDepot_screen.id):
            x = random.randint(0,60)
            y = random.randint(0,60)
            return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (x, y))

        SCV = self.get_units_by_type(obs,units.Terran.SCV)
        if len(SCV) > 0:
          SCV = random.choice(SCV)
          return actions.FUNCTIONS.select_point("select_all_type", (abs(SCV.x), abs(SCV.y)))

  def my_barracks(self, obs):
    barracks = self.get_units_by_type(obs, units.Terran.Barracks)

    if len(barracks) < 3:
        if self.unit_type_is_selected(obs, units.Terran.SCV):       
          if self.can_do(obs,actions.FUNCTIONS.Build_Barracks_screen.id):
            x = random.randint(0,60)
            y = random.randint(0,60)
            return actions.FUNCTIONS.Build_Barracks_screen("now", (x, y))      

        SCV = self.get_units_by_type(obs,units.Terran.SCV)
        if len(SCV) > 0:
          SCV = random.choice(SCV)
          return actions.FUNCTIONS.select_point("select_all_type", (abs(SCV.x), abs(SCV.y)))                   

  def my_refinery(self, obs):
    refinery = self.get_units_by_type(obs, units.Terran.Refinery)
    if len (refinery) == 0 :
        if self.unit_type_is_selected(obs, units.Terran.SCV):        
            if self.can_do(obs,actions.FUNCTIONS.Build_Refinery_screen.id):
                geysers = self.get_units_by_type(obs, units.Neutral.VespeneGeyser)
                if len(geysers) > 0 :
                    geyser = random.choice(geysers)
                    #VespeneGeyser
                    return actions.FUNCTIONS.Build_Refinery_screen("now", (abs(geyser.x),abs(geyser.y)))

        SCV = self.get_units_by_type(obs,units.Terran.SCV)
        if len(SCV) > 0:
          SCV = random.choice(SCV)
          return actions.FUNCTIONS.select_point("select_all_type", (abs(SCV.x), abs(SCV.y)))                   


  def my_idle_workers(self,obs):

    refinery = self.get_units_by_type(obs, units.Terran.Refinery)
    mineral  = self.get_units_by_type(obs, units.Neutral.MineralField)
    command_center = self.get_units_by_type(obs, units.Terran.CommandCenter)
    command_center = random.choice(command_center)
    if self.unit_type_is_selected(obs, units.Terran.SCV) and (len(obs.observation.single_select) < 2 and len(obs.observation.multi_select) < 2) and self.scv_sent_to_harvest==False:    
        if(len(refinery)>0):
          refinery = random.choice(refinery)
          if refinery['assigned_harvesters'] < 2:
            if self.can_do(obs,actions.FUNCTIONS.Harvest_Gather_screen.id):                   
              self.scv_sent_to_harvest=True
              return actions.FUNCTIONS.Harvest_Gather_screen("now",(abs(refinery.x), abs(refinery.y)))
        if command_center['assigned_harvesters'] < 10:
          if(len(mineral)>0):
            mineral = random.choice(mineral)
            if self.can_do(obs,actions.FUNCTIONS.Harvest_Gather_screen.id):                   
              self.scv_sent_to_harvest=True
              return actions.FUNCTIONS.Harvest_Gather_screen("now",(abs(mineral.x), abs(mineral.y)))
    else:
      self.scv_sent_to_harvest=False
      self.camera=True
      return actions.FUNCTIONS.select_idle_worker("select")

  def my_upgrade_marines1(self,obs):
    if self.unit_type_is_selected(obs, units.Terran.BarracksTechLab):
      if self.can_do(obs, actions.FUNCTIONS.Research_CombatShield_quick.id):
        self.upgrade_combatshield=True
        return actions.FUNCTIONS.Research_CombatShield_quick("now")
     
    techlab = self.get_units_by_type(obs, units.Terran.BarracksTechLab)
    if len(techlab)>0 and self.upgrade_combatshield==False:
      print("MarineUpgrade")         
      techlab = random.choice(techlab)
      return actions.FUNCTIONS.select_point("select_all_type", (abs(techlab.x), abs(techlab.y)))


  def upgrade_barracks_techlab(self,obs):
    if self.unit_type_is_selected(obs, units.Terran.Barracks):
      if self.can_do(obs, actions.FUNCTIONS.Build_TechLab_quick.id):
        print("TechLab")
        return actions.FUNCTIONS.Build_TechLab_quick("now")    
    
    barracks = self.get_units_by_type(obs, units.Terran.Barracks)     
    if len(barracks) > 0:
      barracks = random.choice(barracks)
      return actions.FUNCTIONS.select_point("select_all_type", (abs(barracks.x), abs(barracks.y)))


  def upgrade_barracks_reactor(self,obs):
    if self.unit_type_is_selected(obs, units.Terran.Barracks) and self.reactor_built==False:
      if self.can_do(obs, actions.FUNCTIONS.Build_Reactor_quick.id):
        print("Reactor")
        self.reactor_built=True
        return actions.FUNCTIONS.Build_Reactor_quick("now")    

    barracks = self.get_units_by_type(obs, units.Terran.Barracks)     
    if len(barracks) > 0:
      barracks = random.choice(barracks)
      return actions.FUNCTIONS.select_point("select_all_type", (abs(barracks.x), abs(barracks.y)))

#    if self.rally_units==False:
#      if self.can_do(obs, actions.FUNCTIONS.Rally_Units_minimap.id):
#        self.rally_units=True        
#        return actions.FUNCTIONS.Rally_Units_minimap(0,(34,34))


  def train_units(self,obs,type):   

    if type == "marine":
      if self.unit_type_is_selected(obs, units.Terran.Barracks):

        if self.can_do(obs, actions.FUNCTIONS.Train_Marine_quick.id):
          return actions.FUNCTIONS.Train_Marine_quick("now")
      else:
        barracks = self.get_units_by_type(obs, units.Terran.Barracks)     
        if len(barracks) > 0:
          barracks = random.choice(barracks)
          return actions.FUNCTIONS.select_point("select_all_type", (abs(barracks.x), abs(barracks.y)))                  
    
    if type == "marauder":

      if self.unit_type_is_selected(obs, units.Terran.Barracks):

        if self.can_do(obs, actions.FUNCTIONS.Train_Marauder_quick.id):
          return actions.FUNCTIONS.Train_Marauder_quick("now")
      else:
        barracks = self.get_units_by_type(obs, units.Terran.Barracks)     
        if len(barracks) > 0:
          barracks = random.choice(barracks)
          return actions.FUNCTIONS.select_point("select_all_type", (abs(barracks.x), abs(barracks.y)))          


  def my_attack(self, obs):
    marines = self.get_units_by_type(obs, units.Terran.Marine)
    marauders = self.get_units_by_type(obs, units.Terran.Marauder) 
    print(str(len(marines)) + " x " + str(len(marauders)))    
    if len(marines) >15 and len(marauders) >2:     
      if self.unit_type_is_selected(obs, units.Terran.Marine) or self.unit_type_is_selected(obs, units.Terran.Marauder):
        if self.can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
          self.attack_sent = True
          return actions.FUNCTIONS.Attack_minimap("now", self.attack_coordinates)
      else:
        if self.can_do(obs, actions.FUNCTIONS.select_army.id):
          return actions.FUNCTIONS.select_army("select")

  def my_move_camera(self,obs):
    if (self.camera==True):
      self.camera=False      
      return actions.FUNCTIONS.move_camera(self.base_coordinates)

  def step(self, obs):                                                                #Main function that defines what to do in within timeframe
    super(TerranAgent, self).step(obs)                                               	  #Call 'super' to gain access to inherited methods which is either from a parent or sibling class. 
    
    if obs.first():																	  #Check if first step
      player_y, player_x = (obs.observation.feature_minimap.player_relative ==
                            features.PlayerRelative.SELF).nonzero()
      xmean = player_x.mean()
      ymean = player_y.mean()
      if xmean <= 31 and ymean <= 31:												  #Set attack coordinates
        self.attack_coordinates = (49, 49)
        self.base_coordinates   = (20, 25)
      else:
        self.attack_coordinates = (12, 16)
        self.base_coordinates   = (40, 45)
    
    if actions.FUNCTIONS.select_idle_worker.id in obs.observation["available_actions"]:    
      idle_workers = self.my_idle_workers(obs)
      if idle_workers:
        return idle_workers

    move_camera=self.my_move_camera(obs)
    if move_camera:
      return move_camera

    refinery = self.my_refinery(obs)
    if refinery:
      return refinery

    supply_depot = self.my_supply_depot(obs)
    if supply_depot:
      return supply_depot

    barracks = self.my_barracks(obs)
    if barracks:
      return barracks     

    tech_labs=len(self.get_units_by_type(obs, units.Terran.BarracksTechLab))
    reactors=len(self.get_units_by_type(obs, units.Terran.BarracksReactor))      

    if(tech_labs==0):
      tech_lab = self.upgrade_barracks_techlab(obs)
      if tech_lab:
        return tech_lab 
    
#    if(reactors==0):    
#      reactor = self.upgrade_barracks_reactor(obs)
#      if reactor:
#        return reactor 

    if(tech_labs>0):
      marauders =  self.get_units_by_type(obs, units.Terran.Marauder)
      marines =  self.get_units_by_type(obs, units.Terran.Marine)
      
      if len(marauders)>0 and self.upgrade_combatshield==False:

        if(self.upgrade_combatshield==False):
          upgrade_marines1 = self.my_upgrade_marines1(obs)
          if upgrade_marines1:
            return upgrade_marines1
   

      attack = self.my_attack(obs)
      if attack:
        return attack

      if len(marauders)>0 and len(marines)<=15:
        make_units = self.train_units(obs,"marine")
        if make_units:
            return make_units

      if len(marauders) <= 6:
        make_units = self.train_units(obs,"marauder")
        if make_units:
            return make_units




    return actions.FUNCTIONS.no_op()  #do not do anything if there were no matches
def main(unused_argv):
  agent = TerranAgent()                                                                 #Start agent
  try:
    while True:                                                                       #Run function indefinitely
      with sc2_env.SC2Env(                                                            #Setup environment

          map_name="Simple64",                                                        
#AbyssalReef
          players=[sc2_env.Agent(sc2_env.Race.terran),                                  #Player 1 is agent, player 2 is a very easy bot
                   sc2_env.Bot(sc2_env.Race.random,                                   #It's possible to change 'Bot' to 'Agent' for another agent
                               sc2_env.Difficulty.medium)],          

          agent_interface_format=features.AgentInterfaceFormat(
              feature_dimensions=features.Dimensions(screen=84, minimap=64),          #Screen and minimap resolutions
              use_feature_units=True),                                                #Feature units list

          step_mul=16,
          game_steps_per_episode=0,                    
          visualize=True) as env:

        agent.setup(env.observation_spec(), env.action_spec())
        
        timesteps = env.reset()
        agent.reset()
        
        while True:
          step_actions = [agent.step(timesteps[0])] 
          if timesteps[0].last():
            break
          timesteps = env.step(step_actions)
      
  except KeyboardInterrupt:
    pass
  
if __name__ == "__main__":
  app.run(main)      