import sc2

import random

from sc2.constants import *

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.helpers import ControlGroup

class RolloutBot(sc2.BotAI):
    def __init__(self):
        self.SCV_counter = 0
        self.refinerys = 0
        self.barracks_started = False
        self.made_workers_for_gas = False
        self.attack_groups = set()
        
    async def on_step(self, iteration):
        if iteration == 0:
            if iteration == 0:
                await self.chat_send("(glhf)")

#for selecting our Units

        if self.units(REAPER).idle.amount > 14:
            cg = ControlGroup(self.units(REAPER).idle)
            self.attack_groups.add(cg)
            
        for cc in self.units(UnitTypeId.COMMANDCENTER).ready.noqueue:    
            if self.can_afford(SCV) and self.workers.amount < 20 and cc.noqueue:
                await self.do(cc.train(SCV))
        
        cc = self.units(COMMANDCENTER).ready.first
        bobthebuilder = self.units(SCV)[0]
        
#We must construct additional pylons
        if self.supply_left < 2:
            if self.can_afford(SUPPLYDEPOT) and self.already_pending(SUPPLYDEPOT) < 2:
                await self.build(SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 5))
        
#For building reapers     
        if self.units(BARRACKS).amount < 3 or (self.minerals > 400 and self.units(BARRACKS).amount < 5):
            if self.can_afford(BARRACKS):
                err = await self.build(BARRACKS, near=cc.position.towards(self.game_info.map_center, 5))       
           
        elif self.units(BARRACKS).ready.exists and self.units(REFINERY).ready.exists:
            barracks = self.units(BARRACKS).ready
            if self.can_afford(REAPER) and barracks.noqueue:
                await self.do(barracks.random.train(REAPER))
        
        '''        
        if self.units(MISSILETURRET).amount < 3:
            if self.can_afford(MISSILETURRET):
                err = await self.build(MISSILETURRET, near=cc.position.towards(self.game_info.map_center, 5))  
        
        if self.units(ENGINEERINGBAY).amount < 1:
            if self.can_afford(ENGINEERINGBAY):
                err = await self.build(ENGINEERINGBAY, near=cc.position.towards(self.game_info.map_center, 5))        
        '''
        
        if self.refinerys < 2:
            if self.can_afford(REFINERY):
                worker = self.workers.random
                target = self.state.vespene_geyser.closest_to(worker.position)
                err = await self.do(bobthebuilder.build(REFINERY, target))
                if not err:
                    self.refinerys += 1
        
        for a in self.units(REFINERY):
            if a.assigned_harvesters < a.ideal_harvesters:
                w = self.workers.closer_than(20, a)
                if w.exists:
                    await self.do(w.random.gather(a))
                    
        for ac in list(self.attack_groups):
            alive_units = ac.select_units(self.units)
            if alive_units.exists:
                target = self.known_enemy_units.random_or(self.enemy_start_locations[0]).position
                for reaper in ac.select_units(self.units):
                    if reaper.health < reaper.health_max-15:                 
                        await self.do(reaper.move(cc.position))
                    elif reaper.health == reaper.health_max:
                        await self.do(reaper.attack(target))
            else:
                self.attack_groups.remove(ac)
                
        
        
run_game(maps.get("Simple64"), [
    Bot(Race.Terran, RolloutBot()),
    Computer(Race.Zerg, Difficulty.Medium)
], realtime=False)
