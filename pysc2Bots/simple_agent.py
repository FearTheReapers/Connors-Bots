from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

import random
import time

# Functions
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_BUILD_REFINERY = actions.FUNCTIONS.Build_Refinery_screen.id
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id

_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id

_TRAIN_REAPER = actions.FUNCTIONS.Train_Reaper_quick.id
_TRAIN_SCV = actions.FUNCTIONS.Train_SCV_quick.id

_RALLY_WORKERS_SCREEN = actions.FUNCTIONS.Rally_Workers_screen.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id
_RALLY_UNITS_SCREEN = actions.FUNCTIONS.Rally_Units_screen.id

_HARVEST_GATHER_SCREEN = actions.FUNCTIONS.Harvest_Gather_screen.id



# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

# Unit IDs
_TERRAN_COMMANDCENTER = 18
_TERRAN_SUPPLYDEPOT = 19
_TERRAN_REFINERY = 20
_TERRAN_SCV = 45
_TERRAN_REAPER = 49
_TERRAN_BARRACKS = 21
_NEUTRAL_VESPENE_GEYSER = 342


# Parameters
_PLAYER_SELF = 1
_NOT_QUEUED = [0]
_QUEUED = [1]

_MINERALS = 1
_VESPENE = 2
_SUPPLY_USED = 3
_SUPPLY_MAX = 4



class SimpleAgent(base_agent.BaseAgent):

    base_top_left = None
    
    barracks_built = False
    refinery_built = False
    supply_depot_built = False
    
    scv_selected = False
    barracks_selected = False
    command_selected = False
    refinery_selected = False
    army_selected = False
    
    barracks_rallied = False
    command_rallied = False
    
    enemies_onscreen  = False
    scvcount = 13
    refinery_stocked = 0
    refinery_xy = [0, 0]
    scv_index = 1
    numReapers = 0
    count = 0
    rollout = False
    
    

    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]

        return [x + x_distance, y + y_distance]
##
##
###
###
####
##### Begin Agent
    def step(self, obs):
        super(SimpleAgent, self).step(obs)
        
        time.sleep(0)
        
# set our relative base position 
        if not self.rollout:  
            if self.base_top_left is None:
                player_y, player_x = (obs.observation["minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
                self.base_top_left = player_y.mean() <= 31
            

            

    #building supply depots
            if not self.supply_depot_built:
                if not self.scv_selected:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()
                    #selecting a unit involves finding its coordinates using obs.observation

                    target = [unit_x[0], unit_y[0]]

                    self.scv_selected = True

                    return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
                elif _BUILD_SUPPLYDEPOT in obs.observation["available_actions"]:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                    target = self.transformLocation(int(unit_x.mean()), 0, int(unit_y.mean()), 20)

                    self.supply_depot_built = True
                    self.scv_selected = False
                    return actions.FunctionCall(_BUILD_SUPPLYDEPOT, [_NOT_QUEUED, target])
                    

    #building the refinery
            elif not self.refinery_built:
                if _BUILD_REFINERY in obs.observation["available_actions"]:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    vespene_y, vespene_x = (unit_type == _NEUTRAL_VESPENE_GEYSER).nonzero()
                    
                    x = vespene_x[0:97].mean()
                    y = vespene_y[0:97].mean()
                    
                    self.refinery_xy = [x, y]
                
                    self.refinery_built = True
                    
                    return actions.FunctionCall(_BUILD_REFINERY, [_QUEUED, self.refinery_xy])
            
            
            elif not self.barracks_built:
                if _BUILD_BARRACKS in obs.observation["available_actions"]:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                    target = self.transformLocation(int(unit_x.mean()), 25, int(unit_y.mean()), 0)

                    self.barracks_built = True
                    self.scv_selected = False
                    return actions.FunctionCall(_BUILD_BARRACKS, [_QUEUED, target])
            
            elif not self.command_rallied and self.barracks_built:
                if not self.refinery_selected:#refinery has finished building
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _TERRAN_REFINERY).nonzero()
                    
                    if unit_y.any():
                        target = [int(unit_x.mean()), int(unit_y.mean())]
                        self.refinery_selected = True
                        return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
                    
                elif not self.command_selected:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                    if unit_y.any():
                        target = [int(unit_x.mean()), int(unit_y.mean())]

                        self.command_selected = True
                        
                        return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
                        
                elif _RALLY_WORKERS_SCREEN in obs.observation["available_actions"]:
                    self.command_rallied = True
                    self.command_selected = False
                    return actions.FunctionCall(_RALLY_WORKERS_SCREEN, [_NOT_QUEUED, self.refinery_xy])
            
            elif self.command_rallied and self.refinery_stocked < 3:
                print("stuck at command rallied")
                if not self.command_selected:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                    if unit_y.any():
                        target = [int(unit_x.mean()), int(unit_y.mean())]

                        self.command_selected = True

                        return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
                        
                elif _TRAIN_SCV in obs.observation["available_actions"] and self.refinery_stocked < 3:
                    self.refinery_stocked += 1
                    if self.refinery_stocked == 3:
                        self.command_selected = False
                    return actions.FunctionCall(_TRAIN_SCV, [_QUEUED])
                                
    #Rally barracks
            elif not self.barracks_rallied:
                if not self.barracks_selected:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()

                    if unit_y.any():
                        target = [int(unit_x.mean()), int(unit_y.mean())]

                        self.barracks_selected = True

                        return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
                else:
                    self.barracks_rallied = True
                    self.barracks_selected = False
                    self.rollout = 1
                    if self.base_top_left:
                        return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, [29, 21]])

                    return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, [29, 46]])

        else:                    
    #Making reapers
            
            if obs.observation["player"][_SUPPLY_USED] < obs.observation["player"][_SUPPLY_MAX] and _TRAIN_REAPER in obs.observation["available_actions"]:
                if not self.barracks_selected:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()

                    if unit_y.any():
                        target = [int(unit_x.mean()), int(unit_y.mean())]

                        self.barracks_selected = True

                        return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
                elif not self.army_selected:
                    if _SELECT_ARMY in obs.observation["available_actions"]:
                        self.army_selected = True
                        return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])

                selcted = obs.observation["minimap"][6]
                unit_y, unit_x = (selected == 1).nonzero()  
                print(unit_x)  
                if len(obs.observation["minimap"][6])<8 and obs.observation["player"][_MINERALS] > 50 and obs.observation["player"][_VESPENE] > 50:
                    self.numReapers += 1
                    return actions.FunctionCall(_TRAIN_REAPER, [_QUEUED])
        
#now we should have enough reapers
            self.barracks_selected = False
#Time to get our reapers over to the enemies
            if obs.observation["player"][_SUPPLY_USED] == obs.observation["player"][_SUPPLY_MAX]:
                if not self.army_selected:
                    if _SELECT_ARMY in obs.observation["available_actions"]:
                        self.army_selected = True
                        return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])
                
                elif self.army_selected and not self.enemies_onscreen:
                    if _ATTACK_MINIMAP in obs.observation["available_actions"]:
                        if self.base_top_left:
                            return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [39, 45]])
                    
                        return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [21, 24]])
                
             
            
            
            


        return actions.FunctionCall(_NOOP, [])



