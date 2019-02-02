import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.data import race_townhalls


class Human(sc2.BotAI):
    def __init__(self):
        self.alive = True
    
    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("GLHF")



class JoeBot(sc2.BotAI):
    def __init__(self):
        self.drone_counter = 12
        self.spawning_pool = False 
        self.extractor_started = False 
        self.metabolic_boost_started = False 
        self.gas_populated = False 
        self.evolution_chamber_started = False 
        self.zerg_overload_started = False 
        self.zergling_count = 0
        self.zerg_armor_started = False 
        self.lair = True
        self.melee2 = True
        self.queen_count = 0
        self.attack_req = 10

    async def build_workers(self):
        if self.can_afford(DRONE) and self.units(LARVA).exists:
            await self.do(self.units(LARVA).random.train(DRONE))
            self.drone_counter += 1

    async def spawn_overlord(self):
            if self.can_afford(OVERLORD) and self.supply_left < 2 and self.units(LARVA).exists:
                await self.do(self.units(LARVA).random.train(OVERLORD))

    async def expand(self):
        if self.can_afford(NEXUS):
            await self.expand_now()
            self.drone_counter -= 1 

    async def build_extractor(self):
        if True:
            if self.can_afford(EXTRACTOR):
                drone = self.workers.random
                target = self.state.vespene_geyser.closest_to(drone.position)
                err = await self.do(drone.build(EXTRACTOR, target))
                if not err:
                    self.drone_counter -= 1 
                    self.extractor_started = True
    
    async def populate_gas(self):
        extractor = self.units(EXTRACTOR).first
        for drone in self.workers.random_group_of(3):
            await self.do(drone.gather(extractor))
            self.gas_populated = True
        
    async def spawn_zergling(self):
        if self.can_afford(ZERGLING) and self.spawning_pool == True and self.units(LARVA).exists and self.drone_counter > 30:
            await self.do(self.units(LARVA).random.train(ZERGLING))
            self.zergling_count += 1 

    async def build_spawning_pool(self):
        if self.can_afford(SPAWNINGPOOL) and self.spawning_pool == False:
            for d in range(4,15):
                pos = self.units(HATCHERY).ready.first.position.to2.towards(self.game_info.map_center, d)
                if await self.can_place(SPAWNINGPOOL, pos):
                    drone = self.workers.closest_to(pos)
                    err = await self.do(drone.build(SPAWNINGPOOL, pos))
                    if not err:
                        self.spawning_pool = True 
                        break
    async def upgrade_zerg_speed(self):
        if self.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST) and self.metabolic_boost_started == False and self.extractor_started == True:
            await self.do(self.units(SPAWNINGPOOL).ready.first(RESEARCH_ZERGLINGMETABOLICBOOST))
            self.metabolic_boost_started = True 

    async def build_evolution_chamber(self):
        if self.can_afford(EVOLUTIONCHAMBER) and self.evolution_chamber_started == False:
            for d in range(4,15):
                pos = self.units(HATCHERY).ready.first.position.to2.towards(self.game_info.map_center,d)
                if await self.can_place(EVOLUTIONCHAMBER, pos):
                    drone = self.workers.closest_to(pos)
                    err = await self.do(drone.build(EVOLUTIONCHAMBER, pos))
                    if not err:
                        self.evolution_chamber_started = True 
                        break 

    async def upgrade_zergling_power(self):
        if self.can_afford(RESEARCH_ZERGMELEEWEAPONSLEVEL1) and self.zerg_overload_started == False:
            await self.do(self.units(EVOLUTIONCHAMBER).ready.first(RESEARCH_ZERGMELEEWEAPONSLEVEL1))
            self.zerg_overload_started = True 

    async def zergling_attack(self):
        if self.units(ZERGLING).amount > self.attack_req:
            for unit in self.units(ZERGLING):
                await self.do(unit.attack(self.enemy_start_locations[0]))
                self.attack_req += 10

    async def upgrade_zergling_defense(self):
        if self.can_afford(RESEARCH_ZERGGROUNDARMORLEVEL1) and self.zerg_armor_started == False:
            await self.do(self.units(EVOLUTIONCHAMBER).ready.first(RESEARCH_ZERGGROUNDARMORLEVEL1))
            self.zerg_armor_started = True

    async def upgrade_to_lair(self):
        if self.can_afford(LAIR) and self.lair == False and self.townhalls.first.noqueue:
            await self.do(self.townhalls.first.build(LAIR))
            self.lair = True
    
    async def create_queen(self):
        if self.can_afford(QUEEN) and self.queen_count < 5:
            await self.do(self.townhalls.first.train(QUEEN))
            self.queen_count += 1 

    async def upgrade_zergling_power2(self):
        if self.can_afford(RESEARCH_ZERGMELEEWEAPONSLEVEL2) and self.zerg_overload_started == True and self.lair == True:
            await self.do(self.units(EVOLUTIONCHAMBER).ready.first(RESEARCH_ZERGMELEEWEAPONSLEVEL2))
            self.melee2 = True


    async def on_step(self,iteration):
        if iteration == 0:
            await self.chat_send("GLHF")
        await self.upgrade_zerg_speed()
        await self.upgrade_to_lair()
        await self.build_evolution_chamber()
        await self.upgrade_zergling_power()
        await self.upgrade_zergling_defense()
        await self.upgrade_zergling_power2()
        await self.create_queen()
        await self.spawn_zergling()
        await self.distribute_workers()
        await self.build_spawning_pool()
        await self.build_workers()
        await self.spawn_overlord()
        await self.expand()
        await self.build_extractor()
        await self.zergling_attack()



    
# human v bot
# run_game(maps.get("(2)AcidPlantLE"), [
# Bot(Race.Terran, Human()),Bot(Race.Zerg, JoeBot())], realtime=True)

run_game(maps.get("(2)AcidPlantLE"), [
Bot(Race.Zerg, JoeBot()), Computer(Race.Terran, Difficulty.Medium)], realtime=True)
