from discord.ext import tasks, commands
import asyncio

class SonidoLoop(commands.Cog):
    def __init__(self):
      print("Iniciando Loop")

    #COMIENZA EL LOOP
    def start(self, dic,channel, reproduccion_aleatoria, reproducir):
      self.sonido_loop.start(dic,channel, reproduccion_aleatoria, reproducir)

    #PARA EL LOOP
    async def stop(self):
      await asyncio.sleep(1)
      self.sonido_loop.cancel()

    #ESTE ES EL LOOP
    @tasks.loop(seconds = 20)
    async def sonido_loop(self, dic,channel, reproduccion_aleatoria, reproducir):
    
      cancion = await reproduccion_aleatoria(dic)
      await reproducir(channel, cancion  , dic)
