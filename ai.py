import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *


class JoeBot(sc2.BotAI):
    def __init__(self):
        self.drone_counter = 14
        self.spawning_pool = False 
        self.extractor_started = False 
        self.metabolic_boost_started = False 

    async def build_workers(self):
        if self.can_afford(DRONE) and self.drone_counter < 16:
            await self.do(self.units(LARVA).random.train(DRONE))
            self.drone_counter += 1

    async def spawn_overlord(self):
            if self.can_afford(OVERLORD) and self.supply_left < 2:
                await self.do(self.units(LARVA).random.train(OVERLORD))

    async def expand(self):
        if self.can_afford(NEXUS):
            await self.expand_now()
            self.drone_counter -= 1 

    async def build_extractor(self):
        if not self.extractor_started:
            if self.can_afford(EXTRACTOR):
                drone = self.workers.random
                target = self.state.vespene_geyser.closest_to(drone.position)
                err = await self.do(drone.build(EXTRACTOR, target))
                if not err:
                    self.drone_counter -= 1 
                    self.extractor_started = True
        
    async def spawn_zergling(self):
        if self.can_afford(ZERGLING):
            await self.do(self.units(LARVA).random.train(ZERGLING))

    async def build_spawning_pool(self):
        if self.can_afford(SPAWNINGPOOL):
            for d in range(4,15):
                pos = self.units(HATCHERY).ready.first.position.to2.towards(self.game_info.map_center, d)
                if await self.can_place(SPAWNINGPOOL, pos):
                    drone = self.workers.closest_to(pos)
                    err = await self.do(drone.build(SPAWNINGPOOL, pos))
                    if not err:
                        self.spawning_pool = True 
                        break
    async def upgrade_zerg_speed(self):
        if self.can_afford(METABOLICBOOST) and self.metabolic_boost_started == False and self.extractor_started == True:
            await self.do(self.units(SPAWNINGPOOL).ready.first(RESEARCH_ZERGLINGMETABOLICBOOST))
            self.metabolic_boost_started = True 

    async def on_step(self,iteration):
        if iteration == 0:
            await self.chat_send("GLHF")
        if self.drone_counter > 12 and self.spawning_pool == True and self.units(LARVA).exists:
            await self.spawn_zergling()
        await self.distribute_workers()
        if self.spawning_pool == False:
            await self.build_spawning_pool()
        if self.units(LARVA).exists:
            await self.build_workers()
            await self.spawn_overlord()
        await self.expand()
        await self.build_extractor()



# change map name 
run_game(maps.get("(2)AcidPlantLE"), [
Bot(Race.Zerg, JoeBot()),
Computer(Race.Terran, Difficulty.Easy)
], realtime=True)
