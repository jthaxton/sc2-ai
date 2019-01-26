import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON


class JoeBot(sc2.BotAI):
    async def build_workers():
        for nexus in self.units(NEXUS).ready:
            if self.can_afford(DRONE):
                await self.do(nexus.train(DRONE))

    async def spawn_overlord(self):
        for nexus in self.units(NEXUS).ready:
            if self.can_afford(OVERLORD):
                await self.do(nexus.train(OVERLORD))

    async def expand(self):
        if self.can_afford(NEXUS):
            await self.expand_now()

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

    async def on_step(self,iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.expand()
        await self.build_assimilator()


# change map name 
run_game(maps.get("AbyssalReefLE"), [
Bot(Race.Zerg, SentdeBot()),
Computer(Race.Terran, Difficulty.Easy)
], realtime=True)