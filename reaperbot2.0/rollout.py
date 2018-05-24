import sc2

import random
from collections import defaultdict

from sc2.constants import *

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.helpers import ControlGroup
weight = [1,2,3]
    

class RolloutBot(sc2.BotAI):
    def __init__(self, weights):
        self.SCV_counter = 0
        self.refinerys = 0
        self.barracks_started = False
        self.made_workers_for_gas = False
        self.attack_groups = set()
        self.reaper_health = {}
        self.enemy_health = {}
        self.reapergenes = defaultdict(list)
        self.reaperrewards = {}
        self.reaper_indexer = {}
        self.seed = weights
        self.reaperlasttarget = {}
        self.reaperlasttargethealth = {}
        
    async def on_step(self, iteration):
        if iteration == 0:
            if iteration == 0:
                await self.chat_send("(glhf)")

#for selecting our Units

        if self.units(REAPER).idle.amount > 10:
            for reaper in self.units(REAPER).idle:
                #mutate reaper genes
                if(not self.reaperrewards):
                    self.seed[0] = weights[0]*(random.randint(1,200)/100)
                    self.seed[1] = weights[1]*(random.randint(1,200)/100)
                    self.seed[2] = weights[2]*(random.randint(1,200)/100)
                    self.reapergenes[reaper.tag] = self.seed
                else:
                    for guy in reaperrewards
                    self.seed[0] = weights[0]*(random.randint(1,200)/100)
                    self.seed[1] = weights[1]*(random.randint(1,200)/100)
                    self.seed[2] = weights[2]*(random.randint(1,200)/100)
                    self.reapergenes[reaper.tag] = self.seed
                    
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
        
        #TODO hash the reapers with info on health wieghts
        #TODO hash the enemy health totals to reward focusing
        #TODO reward reaper health maximization by hashing reaper health changes
        #TODO Create population
        #genes relevant to reaper movement
        #reaper attack allocation
            #weight for 
        #
        #
                    
        for ac in list(self.attack_groups):
            alive_units = ac.select_units(self.units)
            total_x = []
            total_y = []
            total_z = []
            if alive_units.amount > 5:
                for reaper in ac.select_units(self.units):
                    ting = 10
                    targets = self.known_enemy_units.prefer_close_to(reaper)
                    self.enemyreward = {}
                    self.enemyindexer = {}
                    for enemy in targets:
                        if ting == 0:
                            break
                        self.enemyindexer[enemy.tag] = enemy
                        #the negative 1 gives more reward for enemies that are easily killed by your team
                        self.enemyreward[enemy.tag] = -1*(enemy.health-alive_units.amount*8)*self.reapergenes[reaper.tag][1]
                        #since they are already in order of closeness we can add a value for being closest
                        #and decrement it each time to give different rewards
                        self.enemyreward[enemy.tag] += self.reapergenes[reaper.tag][2]*(ting)
                        
                        ting -= 1
                
                if(targets.exists):
                    v = list(self.enemyreward.values())
                    k = list(self.enemyreward.keys())
                    target = self.enemyindexer[k[v.index(max(v))]]
                else:
                    target = self.enemy_start_locations[0]
                    
                for reaper in ac.select_units(self.units):
                    if(reaper.tag in self.reaper_health):
                        if  reaper.health < self.reaper_health[reaper.tag]:                
                            await self.do(reaper.move(reaper.position.towards(target.position, self.reapergenes[reaper.tag][2]*-5)))
                        elif  reaper.health < reaper.health_max:
                            await self.do(reaper.move(barracks.random.position))
                        elif reaper.is_idle:
                            await self.do(reaper.attack(target))
                            
                    reaperrewards[reaper.tag] = 100 - (self.reaper_health[reaper.tag] - reaper.health)
                    if reaper.tag in self.reaperlasttarget:
                        if not self.reaperlasttarget[reaper.tag].exists:
                            reaperrewards[reaper.tag] += 100
                        elif self.reaperlasttarget[reaper.tag].health < self.reaperlasttargethealth[reaper.tag]:
                            reaperrewards[reaper.tag] += .1*self.reaperlasttargethealth[reaper.tag] - self.reaperlasttarget[reaper.tag].health
                            
                    self.reaperlasttarget[reaper.tag] = target
                    self.reaperlasttargethealth[reaper.tag] = target.health
                    self.reaper_health[reaper.tag] = reaper.health
            else:
                for reaper in ac.select_units(self.units):
                    await self.do(reaper.move(cc.position))
                self.attack_groups.remove(ac)
                
        
        
run_game(maps.get("Simple64"), [
	Bot(Race.Terran, RolloutBot([1,2,3])),
	Computer(Race.Zerg, Difficulty.Medium)
], realtime=False)
