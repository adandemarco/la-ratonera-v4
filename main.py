import os
import discord
from discord.ext import tasks, commands
import random
import time
import asyncio
from discord import FFmpegPCMAudio
from loop import SonidoLoop


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

dic_audios = {}
dic_audios_no_repe = {}
dic_imagenes = {}
dic_coscu = {}

dic_xtiempo = {}
repetidos = []

audios_comandos = "audios_con_comandos"
audios_sin_comandos = "audios_sin_comandos"
audios_coscu = "coscu"

@client.event
async def on_ready():
    client.add_cog(SonidoLoop())

    await actualizar_dic(audios_comandos, dic_audios)
    await actualizar_dic(audios_sin_comandos, dic_audios_no_repe)
    await actualizar_dic(audios_coscu, dic_coscu)
    await actualizar_dic("img", dic_imagenes)

    #EN LA LISTA PONER LOS DICCIONARIOS PARA LA REPRODUCCION ALEATORIA POR TIEMPO
    await crear_dic_tiempo([dic_audios, dic_coscu], dic_xtiempo)
    
    print('We have logged in as {0.user}'.format(client))


async def crear_dic_tiempo(lista, dic):
  for i in lista:
    dic_xtiempo.update(i)


#CREA Y ACTUALIZA LOS DICCIONARIOS------------------------------------
async def actualizar_dic(carpeta, lista):
  a = os.listdir(carpeta)
  for i in a:
    aux = i.split(".")
    if aux[0] not in lista:
      aux = aux[0]
      lista[aux] = carpeta + "/" + i

#ENVIA IMAGENES--------------------------------------------------------
@client.command()
async def i(ctx, imagen):
  await ctx.send(file=discord.File(dic_imagenes[imagen]))
  

#LISTA LOS COMANDOS-----------------------------------------

async def listar(dic,comando):
    mensaje = ""
    claves = dic.keys()
    for i in claves:
        mensaje += "!" + comando + " " + i + ", "

    return mensaje

@client.command()
async def audios(ctx):
  mensaje = await listar(dic_audios,"a")
  await ctx.send(mensaje)

@client.command()
async def caudios(ctx):
  mensaje = await listar(dic_coscu,"coscu")
  await ctx.send(mensaje)

@client.command()
async def imagen(ctx):
  mensaje = await listar(dic_imagenes, "i")
  await ctx.send(mensaje)

#IMAGEN ALEATORIA
@client.command(pass_context=True)
async def img(ctx):
    img_list = os.listdir("img")
    n = random.randint(0, len(img_list) - 1)
    await ctx.send(file=discord.File("img/" + img_list[n]))


@client.command()
async def comandos(ctx):
    #test.start(ctx)
    await ctx.send("ℂ𝕦𝕔𝕙𝕒 𝕡𝕒, 𝕖𝕤𝕥𝕠 𝕖𝕤 𝕝𝕠 𝕢𝕦𝕖 𝕡𝕠𝕕𝕖𝕤 𝕙𝕒𝕔𝕖𝕣:\n \
𝐀𝐮𝐝𝐢𝐨𝐬: \
!a vergac !a cuandovemos !a verga !a holayogi !a uy !a papada !a trans !a 300\
!a gaben !a tendencia !a naruto !a jaja !a fernando !a despierta !a risa !a dayo\
!a torta !a noo !a paja !a cagando !a dametodo !a grandesanti !a esteban !a chikita\
!a afirmacion\
\n \
𝐈𝐦𝐚𝐠𝐞𝐧𝐞𝐬: \
!i callacagada !i damn !i escracho !i ogt !i ratonera !i ventilador ")


#CORTA EL AUDIO-------------------------------------------------------
def parar_audio():
  global cortar_audio
  cortar_audio = True
 

#REPDORUDIR-----------------------------------------------------------
async def reproducir(channel, cancion, dic_aux):
  global cortar_audio
  cortar_audio = False

  voice = await channel.connect()
  
  if not voice.is_playing():
    source = FFmpegPCMAudio( dic_aux[cancion])
    player = voice.play(source)

  while voice.is_playing() and not cortar_audio:

    await asyncio.sleep(1)
    
  await voice.disconnect()

@client.command()
async def stop(ctx):
  parar_audio()

#COMPROBAR REPETIDO Y MODIFICAR
def cancion_repetida(cancion):
  global repetidos

  if cancion in repetidos:
    return True
  else:
    repetidos.append(cancion)
    if len(repetidos) >= 7:
      repetidos.pop(0)
    return False
  


#GENERA CANCION ALEATORIA-----------------------------------------------
async def reproduccion_aleatoria(dic_aux):
  canciones = list(dic_aux.keys())
  es_repe = True
  cancion = ""
  # print(canciones, len(canciones), dic_xtiempo)
  while(es_repe):  
    n = random.randint(0, len(canciones) - 1)
    cancion = canciones[n]
    es_repe = cancion_repetida(cancion)

  return cancion


# AUTOMATICAMENTE CADA X SEG--------------------------------------------
@client.command()
async def t(ctx,a):
    if a == "on":
      channel = ctx.message.author.voice.channel
      client.cogs["SonidoLoop"].start(dic_xtiempo, channel , reproduccion_aleatoria, reproducir)
      await ctx.send("Timer Encendido")
    elif a == "off":
      parar_audio()
      await client.cogs["SonidoLoop"].stop()
      await ctx.send("Timer Apagado")


#AUDIOS DE COSCU
@client.command(pass_context=True)
async def coscu(ctx, cancion = ""):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel  
        if not cancion:
          cancion = await reproduccion_aleatoria(dic_coscu)
        await reproducir(channel, cancion, dic_coscu)
    else:
        await ctx.send("No estoy en el canal de voz")

#REPRODUCE UN SOLO AUDIO ESPECIFICO
@client.command(pass_context=True)
async def a(ctx, cancion):
    if (ctx.author.voice) and cancion in dic_audios:
        channel = ctx.message.author.voice.channel
        await reproducir(channel, cancion, dic_audios)

#REPRODUCE EN FUNCION DE UNA PALABRA CLAVE
@client.event
async def on_message(message):
    claves = dic_audios_no_repe.keys()
    if client.user.id != message.author.id and ("!" not in message.content):
        cancion = ""
        for i in claves:
            if i in message.content:
                cancion = i
                break
        if cancion:
          channel = message.author.voice.channel
          await reproducir(channel, cancion, dic_audios_no_repe)
    await client.process_commands(message)


client.run(os.environ['TOKEN'])
