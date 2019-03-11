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
        self.spawning_pool = False 
        self.extractor_started = 0 
        self.metabolic_boost_started = False 
        self.gas_populated = False 
        self.evolution_chamber_started = False 
        self.zerg_overload_started = False 
        self.zergling_count = 0
        self.zerg_armor_started = False 
        self.lair = False
        self.melee2 = False
        self.queen_count = 0
        self.attack_req = 10
        self.defense2 = False 
        self.defense3 = False 
        self.melee3 = False 
        self.hive = False
        self.hydralisk_den = False 
        self.infestation_pit = False 

    async def build_workers(self):
        if self.can_afford(DRONE) and self.units(LARVA).exists and self.units(DRONE).amount <= 20:
            await self.do(self.units(LARVA).random.train(DRONE))

    async def spawn_overlord(self):
            if self.can_afford(OVERLORD) and self.supply_left < 2 and self.units(LARVA).exists and self.supply_used <= 200:
                await self.do(self.units(LARVA).random.train(OVERLORD))

    async def expand(self):
        if self.can_afford(NEXUS):
            await self.expand_now()

    async def build_extractor(self):
        if self.can_afford(EXTRACTOR) and self.extractor_started < 5:
            drone = self.workers.random
            target = self.state.vespene_geyser.closest_to(drone.position)
            err = await self.do(drone.build(EXTRACTOR, target))
            if not err:
                self.extractor_started += 1
    
    # async def populate_gas(self):
    #     extractor = self.units(EXTRACTOR).first
    #     for drone in self.workers.random_group_of(3):
    #         await self.do(drone.gather(extractor))
    #         self.gas_populated = True
        
    async def spawn_zergling(self):
        if self.can_afford(ZERGLING) and self.spawning_pool == True and self.units(LARVA).exists and self.units(DRONE).amount > 20:
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
        if self.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST) and self.metabolic_boost_started == False:
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
    
    async def build_hydralisk_den(self):
        if self.can_afford(HYDRALISKDEN) and self.units(LAIR).amount >= 1 and self.units(HYDRALISKDEN).amount < 1:
            for d in range(4,15):
                pos = self.units(LAIR).ready.first.position.to2.towards(self.game_info.map_center,d)
                if await self.can_place(HYDRALISKDEN, pos):
                    drone = self.workers.closest_to(pos)
                    err = await self.do(drone.build(HYDRALISKDEN, pos))
                    if not err:
                        self.hydralisk_den = True
                        break 

    async def upgrade_zergling_power(self):
        if self.can_afford(RESEARCH_ZERGMELEEWEAPONSLEVEL1) and self.zerg_overload_started == False:
            err = await self.do(self.units(EVOLUTIONCHAMBER).ready.first(RESEARCH_ZERGMELEEWEAPONSLEVEL1))
            if err:
                self.zerg_overload_started = True 
            else:
                self.zerg_overload_started = False 

    async def zergling_attack(self):
        if self.units(ZERGLING).amount > 30:
            for unit in self.units(ZERGLING):
                await self.do(unit.attack(self.enemy_start_locations[0]))
                # self.attack_req += 10

    async def upgrade_zergling_defense(self):
        if self.can_afford(RESEARCH_ZERGGROUNDARMORLEVEL1) and self.zerg_armor_started == False:
            await self.do(self.units(EVOLUTIONCHAMBER).ready.first(RESEARCH_ZERGGROUNDARMORLEVEL1))
            self.zerg_armor_started = True

    async def upgrade_to_lair(self):
        if self.can_afford(LAIR) and self.townhalls.first.noqueue and self.units(LAIR).amount < 1:
            await self.do(self.townhalls.first.build(LAIR))
            
    async def create_queen(self):
        if self.can_afford(QUEEN) and self.queen_count < 5:
            await self.do(self.townhalls.first.train(QUEEN))
            self.queen_count += 1 

    async def upgrade_zergling_power2(self):
        if self.can_afford(RESEARCH_ZERGMELEEWEAPONSLEVEL2) and self.zerg_overload_started == True and self.units(LAIR).exists:
            err = await self.do(self.units(EVOLUTIONCHAMBER).ready.first(RESEARCH_ZERGMELEEWEAPONSLEVEL2))
            if err:
                self.melee2 = True
            else:
                self.melee2 = False


    async def upgrade_zergling_power3(self):
        if self.can_afford(RESEARCH_ZERGMELEEWEAPONSLEVEL3) and self.melee2 == True and self.units(HIVE).exists:
            await self.do(self.units(EVOLUTIONCHAMBER).ready.first(RESEARCH_ZERGMELEEWEAPONSLEVEL3))
            self.melee3 = True
        elif self.hive == False:
            await self.upgrade_to_hive()

    async def upgrade_zergling_defense2(self):
        if self.can_afford(RESEARCH_ZERGGROUNDARMORLEVEL2) and self.units(LAIR).exists and self.zerg_armor_started == True:
            await self.do(self.units(EVOLUTIONCHAMBER).ready.first(RESEARCH_ZERGGROUNDARMORLEVEL2))
            self.defense2 = True 
        elif self.lair == False:
            await self.upgrade_to_lair()

    async def upgrade_zergling_defense3(self):
        if self.can_afford(RESEARCH_ZERGGROUNDARMORLEVEL3) and self.units(HIVE).exists and self.defense2 == True:
            await self.do(self.units(EVOLUTIONCHAMBER).ready.first(RESEARCH_ZERGGROUNDARMORLEVEL3))
            self.defense3 = True
        elif self.hive == False:
            await self.upgrade_to_hive()

    async def upgrade_to_hive(self):
        if self.can_afford(HIVE) and self.townhalls.first.noqueue and self.infestation_pit == True and self.units(LAIR).exists and self.units(HIVE).amount < 1:
            await self.do(self.townhalls.first.build(HIVE))
    
    async def build_infestation_pit(self):
        if self.can_afford(INFESTATIONPIT) and self.infestation_pit == False and self.units(LAIR).exists:
            for d in range(4,15):
                pos = self.units(LAIR).ready.first.position.to2.towards(self.game_info.map_center,d)
                if await self.can_place(INFESTATIONPIT, pos):
                    drone = self.workers.closest_to(pos)
                    err = await self.do(drone.build(INFESTATIONPIT, pos))
                    if not err:
                        self.infestation_pit = True
                        break 

    async def spawn_anti_air(self):
        if self.can_afford(HYDRALISK) and self.units(LARVA).exists and self.units(LAIR).exists and self.units(HYDRALISKDEN).amount < 1:
            await self.do(self.units(LARVA).random.train(HYDRALISK))

    async def on_step(self,iteration):
        if iteration == 0:
            await self.chat_send("GLHF")
        await self.upgrade_zerg_speed()
        await self.build_evolution_chamber()
        await self.upgrade_zergling_power()
        await self.upgrade_zergling_defense()
        await self.upgrade_to_lair()
        # await self.build_infestation_pit()
        # await self.upgrade_to_hive()
        if self.units(LAIR).exists:
            await self.upgrade_zergling_power2()
            await self.upgrade_zergling_defense2()
        # if self.units(HIVE).exists:
        #     await self.upgrade_zergling_power3()
        #     await self.upgrade_zergling_defense3()
        await self.build_workers()
        # await self.build_hydralisk_den()
        # await self.create_queen()
        # await self.spawn_anti_air()
        await self.spawn_overlord()
        await self.build_spawning_pool()
        await self.spawn_zergling()
        await self.distribute_workers()
        await self.expand()
        # await self.populate_gas()
        if self.extractor_started < 3:
            await self.build_extractor()
        await self.zergling_attack()





    
# human v bot
# run_game(maps.get("(ƒ2)AcidPlantLE"), [
# Bot(Race.Terran, Human()),Bot(Race.Zerg, JoeBot())], realtime=True)

# bot v ai
run_game(maps.get("(2)AcidPlantLE"), [
Bot(Race.Zerg, JoeBot()), Computer(Race.Terran, Difficulty.Medium)], realtime=True)


