import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *


class JoeBot(sc2.BotAI):
    def __init(self):
        self.drone_counter = 12

    async def build_workers(self):
        if self.can_afford(DRONE) & self.drone_counter < 14:
            await self.do(self.units(LARVA).random.train(DRONE))
            self.drone_counter += 1

    async def spawn_overlord(self):
            if self.can_afford(OVERLORD) & self.supply_left < 2:
                await self.do(self.units(LARVA).random.train(OVERLORD))

    async def expand(self):
        if self.can_afford(NEXUS):
            await self.expand_now()
            self.drone_counter -= 1 

    async def build_assimilator(self):
        for nexus in self.units(NEXUS).ready:
            vespenes = self.state.vespene_geyser.closer_than(25.0, nexus)
            for vespene in vespenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vespene.position)
                if worker is None:
                    break 
                if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
                    await self.do(worker.build(ASSIMILATOR,vespene))
                    self.drone_counter -= 1 
        
    async def spawn_zergling(self):
        if self.can_afford(ZERGLING):
            await self.do(self.units(LARVA).random.train(ZERGLING))


    async def on_step(self,iteration):
        if iteration == 0:
            await self.chat_send("GLHF")

        await self.distribute_workers()
        await self.build_workers()
        await self.spawn_overlord()
        await self.expand()
        await self.build_assimilator()
        await self.spawn_zergling()



# change map name 
run_game(maps.get("(2)AcidPlantLE"), [
Bot(Race.Zerg, JoeBot()),
Computer(Race.Terran, Difficulty.Easy)
], realtime=True)
