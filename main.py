import discord
import random
import os
import requests
import json
import youtube_dl
import numpy
import shutil
import config
import asyncio
from tube_dl import Youtube
from datetime import datetime, timedelta
from discord.ext import commands
from pathlib import Path
from discord.utils import get
from time import sleep
import subprocess


description = '''I am a sucking bot...'''
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', description=description, intents=intents, help_command=None, case_insensitive=False)
guild = discord.Guild
activity = discord.Game(name='Python 3.9')
cemojis = ['sucks']
thonks = ['thonk','thonkpeko','clockthonk','kp','cheweithonk']
memepath = Path('assets/meme')
voicepath = Path('assets/voice')
cachepath = Path('assets/cache')
fdpath = Path('assets/food.csv')
# activity = discord.Activity(name='Books', type=discord.ActivityType.watching)


async def cmdEmoji(ctx, cnl, emoji='👌'):
	cnl = ctx.message.channel
	async for msg in cnl.history(limit=1):
		await msg.add_reaction(emoji)

async def checkConfirm(ctx, msg, emoji='✅'):
	await msg.add_reaction(emoji)
	def check(reaction, user):
		return user == ctx.author and str(reaction.emoji) in [emoji] and reaction.message == msg
	return await client.wait_for('reaction_add', check=check)

def getImg(url, pth, filename, last):
	r = requests.get(url, stream=True)
	if r.status_code == 200:
		r.raw.decode_content = True
		with open(pth / (filename + last), 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		print('Image sucessfully Downloaded: ', filename)
		return 0
	else:
		print('Image Couldn\'t be retreived.')
		return -1


def getNonHiddenFiles(path):
	return [f for f in os.listdir(path) if not f.startswith('.')]


@client.event
async def on_ready():
	await client.change_presence(activity=activity)
	print('Logged in as :')
	print(client.user.name)
	print(client.user.id)
	print('------')


@client.command()
async def help(ctx):
	name = str(client.user.name)
	description = ''
	icon = str(client.user.avatar_url)

	embed = discord.Embed(
		title=name + ' bot help.',
		description=description,
		color=discord.Color.green()
	)
	embed.set_thumbnail(url=icon)
	embed.add_field(name='!hello', value='Say hello to me!', inline=True)
	embed.add_field(name='!server', value='Show server info.', inline=True)
	embed.add_field(name='!eat', value='YumYum, pick some food.', inline=True)
	embed.add_field(name='!meme', value='Show or add memes', inline=True)
	embed.add_field(name='!v', value='Add me to voice channel, yay!', inline=True)
	embed.add_field(name='!invite', value='Create server invite.', inline=True)
	embed.add_field(name='!help', value='Show THIS help.', inline=True)

	await ctx.send(embed=embed)


@client.command()
async def server(ctx):
	name = str(ctx.guild.name)
	description = str(ctx.guild.description)
	owner = str(ctx.guild.owner)
	sid = str(ctx.guild.id)
	region = str(ctx.guild.region)
	membercnt = str(ctx.guild.member_count)
	icon = str(ctx.guild.icon_url)

	embed = discord.Embed(
		title=name + ' Server Info.',
		description=description,
		color=discord.Color.blue()
	)
	embed.set_thumbnail(url=icon)
	embed.add_field(name='Owner', value=owner, inline=True)
	embed.add_field(name='Server ID', value=sid, inline=True)
	embed.add_field(name='Region', value=region, inline=True)
	embed.add_field(name='Member Count', value=membercnt, inline=True)

	await ctx.send(embed=embed)


@client.command()
async def invite(ctx):
	'''Create instant invite'''
	link = await ctx.channel.create_invite(max_age=300)
	await ctx.send('Yay! Here is an invite to your server: ' + link)


@client.command()
async def hello(ctx, arg=''):
	await ctx.send(f'Hello, {ctx.author.mention} !')

def changevol(vc, vol):
	vc.source = discord.PCMVolumeTransformer(vc.source)
	vc.source.volume = vol

def randEat(ls = open(fdpath, 'r',encoding='utf-8').readlines()):
	randeat = random.choice(ls)
	embed = discord.Embed(
	title=randeat,
	color=discord.Color.green()
	)
	return embed


@client.command()
async def v(ctx, arg='', arg2='', arg3=''):
	cnl = ctx.channel
	vc = get(ctx.bot.voice_clients, guild=ctx.guild)
	if arg.startswith('leave'):
		if vc is None:
			await ctx.send('🧐 I am not in any voice channel.')
		else:
			await ctx.voice_client.disconnect()
		await ctx.message.delete()
	elif not arg in ['list', 'add']:
		if vc is None:
			channel = ctx.author.voice.channel
			vc = await channel.connect()
	if arg == 'play':
		await cmdEmoji(ctx, cnl, '📢')
		sfile = voicepath / (arg2 + '.mp3')
		vc.play(discord.FFmpegPCMAudio(executable='C:/ffmpeg/bin/ffmpeg.exe',source=sfile))
		changevol(vc, 0.4)
		while vc.is_playing():
			sleep(.1)
		await ctx.message.delete()
	if arg == 'list':
		vlist = getNonHiddenFiles(voicepath)
		vlist.sort()
		await ctx.send('```' + '\n'.join(vlist) + '```')
	if arg == 'vol':
		if not arg2 =='' and 0 <= int(arg2) <= 100:
			nvol = int(arg2) / 100
		if vc.is_playing():
			changevol(vc, nvol)
	if arg =='add':
		if arg2=='' or arg3=='':
			await cmdEmoji(ctx, cnl, '⚠️')
			return
		await cmdEmoji(ctx, cnl, '📥')
		ydl_opts = {
		'outtmpl': 'assets/voice/' +arg2+ ".%(ext)s",
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
		}
		try:
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				ydl.download([arg3])
		except youtube_dl.utils.DownloadError:
			await cmdEmoji(ctx, cnl, '⚠️')
		if os.path.exists(voicepath / (str(arg2) + '.mp3')):
			await cmdEmoji(ctx, cnl, '✅')
	if arg == 'yt':
		song_there = os.path.isfile(cachepath / 'ytcache.mp3')
		try:
			if song_there:
				os.remove(cachepath / 'ytcache.mp3')
		except PermissionError:
			await ctx.send('Wait for the current playing music to end or use the `!v stop` command')
			return
		print(str(arg2))
		ydl_opts = {
		'outtmpl': 'assets/cache/ytcache.%(ext)s',
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '320',
		}],
		}
		try:
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				ydl.download([arg2])
		except youtube_dl.utils.DownloadError:
			await cmdEmoji(ctx, cnl, '⚠️')
		songpath = cachepath / 'ytcache.mp3'
		vc.play(discord.FFmpegPCMAudio(executable='C:/ffmpeg/bin/ffmpeg.exe', source = songpath))
		changevol(vc, 0.4)
	if arg == 'stop':
		vc.stop()

@client.command()
async def manage(ctx, arg1=''):
	if arg1=='':
		await cmdEmoji(ctx, ctx.channel, '❓')
	if arg1=='stop':
		if str(ctx.author) == 'jc-hiroto#9838':
			await cmdEmoji(ctx, ctx.channel, '💤')
			msg = await ctx.send('⚠️**Shutdown Confirm**')
			c = await checkConfirm(ctx, msg)
			if c:
				await ctx.send('**Shutting down... Bye!** 💤💤💤')
				vc = get(ctx.bot.voice_clients, guild=ctx.guild)
				if vc is not None:
					await vc.disconnect()
				exit(0)
		else:
			await cmdEmoji(ctx, ctx.channel, '🖕')

@client.command()
async def eat(ctx, arg1='', arg2=''):
	cnl = ctx.channel
	if arg1 == '':
		await cmdEmoji(ctx, cnl, '⚠️')
		await ctx.send('🧐 Please enter a argument.\ni.e. `!eat rand` or `!eat add <name>`')
		return
	ffood = open(fdpath, 'r',encoding='utf-8')
	eatlist = ffood.readlines()
	if arg1.startswith('rand'):
		await cmdEmoji(ctx, cnl, '🍽')
		await ctx.send('🧐')
		embed = randEat()
		await ctx.send(f'{ctx.author.mention} 今晚，我想來點')
		async with ctx.typing():
			sleep(1)
		await ctx.send(embed=embed)
	if arg1.startswith('list') :

		await cmdEmoji(ctx, cnl, '🍽')
		await ctx.send('```' + ''.join(eatlist) + '```')

	if arg1.startswith('add') :
		if arg2 == '' :
			await cmdEmoji(ctx, cnl, '⚠️')
			await ctx.send('🧐 Please enter a restaurant name, bruh.\nFormat: `!eat add <name>`')
		elif arg2+'\n' in eatlist:
			await cmdEmoji(ctx, cnl, '⚠️')
			await ctx.send('🧐 This restaurant is already in the list, nice try tho.')
		else:
			with open(fdpath, 'a',encoding='utf-8') as fd:
				fd.write(arg2+'\n')
			await cmdEmoji(ctx, cnl, '🍽')
			await cmdEmoji(ctx, cnl, '✅')
			ffood = open(fdpath, 'r',encoding='utf-8')
			eatlist = ffood.readlines()
			print(eatlist)


@client.command()
async def meme(ctx, arg1='', arg2=''):
	cnl = ctx.channel
	# await cmdsucceed(ctx, cnl)
	if(arg1=='add'):
		find = False
		if(arg2 == ''):
			await cmdEmoji(ctx, cnl, '⚠️')
			await ctx.send('Your meme needs a name.\n⚠️ Please type in the following format:\n`!meme add <meme_name>`')
			return
		if(arg2 in ['add','list','del','!meme']):
			await cmdEmoji(ctx, cnl, '⚠️')
			await ctx.send('⚠️ Do not use the command as the name of meme, nice try tho.')
			return
		if os.path.exists(memepath / (str(arg2) + '.png')) or os.path.exists(memepath / (str(arg2) + '.gif')):
			msg = await ctx.send('`'+arg2+'` already exists.\n⬇ If you want to overwrite, press 📥')
			c = await checkConfirm(ctx, msg, '📥')
		else:
			c = True
		async for msg in cnl.history(limit=10):
			if(msg.author == ctx.author and c):
				if msg.attachments:
					att = msg.attachments[0]
					ofile = att.filename.lower()
					if ofile.endswith('.jpg') or ofile.endswith('.png') or ofile.endswith('.jpeg'):
						find = True
						await msg.add_reaction('📥')
						imgurl = att.url
						filename = arg2
						if getImg(imgurl, memepath, filename, '.png') == 0:
							await msg.add_reaction('✅')
						else:
							await ctx.send("😢 Oof! I can't get this meme pic, plz try again.")
							await msg.add_reaction('⚠️')
						break
					if ofile.endswith('.gif'):
						find = True
						await msg.add_reaction('📥')
						imgurl = att.url
						filename = arg2
						if getImg(imgurl, memepath, filename, '.gif') == 0:
							await msg.add_reaction('✅')
						else:
							await ctx.send("😢 Oof! I can't get this meme pic, plz try again.")
							await msg.add_reaction('⚠️')
						break

		if not find:
			await ctx.send('😢 No supported picture found.\n(Only `.png` & `.jpg` images are accepted and I am only capable of searching 10 latest messages.) :')
	elif arg1=='list':
		imglist = getNonHiddenFiles(memepath)
		imglist.sort()
		await ctx.send('```' + '\n'.join(imglist) + '```')
	elif arg1 == 'del':
		if str(ctx.author) == 'jc-hiroto#9838':
			if os.path.exists(memepath / (str(arg2) + '.png')):
				delpath = memepath / (str(arg2) + '.png')
			elif os.path.exists(memepath / (str(arg2) + '.gif')):
				delpath = memepath / (str(arg2) + '.gif')
			else:
				await cmdEmoji(ctx, cnl, '⚠️')
				return
			confirmmsg = await ctx.send('⚠️ **Delete Confirm**\nAre you sure to delete the meme `'+arg2+'` ?')
			confirm = await checkConfirm(ctx, confirmmsg, '✅')
			if confirm:
				os.remove(delpath)
				await ctx.send('🗑 Deleted.')

		else:
			await cmdEmoji(ctx, cnl, '🖕')
	elif arg1:
		if os.path.exists(memepath / (str(arg1) + '.gif')) or os.path.exists(memepath / (str(arg1) + '.png')):
			sub = '.png'
			if(os.path.exists(memepath / (str(arg1) + '.gif'))):
				sub = '.gif'
			await ctx.message.delete()
			await ctx.send(f'{ctx.author.mention} says: ')
			await ctx.send(file=discord.File(memepath / (str(arg1) + sub)))

	else:
		await cmdEmoji(ctx, cnl, '🔀')
		randimg = random.choice(getNonHiddenFiles(memepath))
		async with ctx.typing():
			sleep(1)
		await ctx.send(file=discord.File(memepath / randimg))

def parseF1race(season, round):
	url = "http://ergast.com/api/f1/"+ season + "/" +round+".json"
	payload={}
	headers = {}
	response = requests.get(url, headers=headers, data=payload)
	j = response.json()
	race = j['MRData']['RaceTable']['Races'][0]
	return race

def parseWikiImg(s):
	purl = s.rsplit('/', 1)[-1]
	print(purl)
	url = "http://en.wikipedia.org/w/api.php?action=query&titles="+purl+"&prop=pageimages&format=json&pithumbsize=500"
	payload={}
	headers = {}
	response = requests.get(url, headers=headers, data=payload)
	j = response.json()
	img = j['query']['pages']
	for i in img:
		img = img[i]
	try:
		imgUrl = img['thumbnail']['source']
	except:
		imgUrl = "https://image.flaticon.com/icons/png/512/65/65578.png"
	return imgUrl

@client.command()
async def f1(ctx, arg1='', arg2=''):
	if(arg1 != '' and arg2 != ''):
		race = parseF1race(arg1, arg2)
		loc = race['Circuit']['Location']['locality']+', '+race['Circuit']['Location']['country']
		dt = datetime.strptime(race['date']+race['time'], "%Y-%m-%d%H:%M:%SZ") + timedelta(hours = 8)
		dts = dt.strftime("%Y/%m/%d %H:%M") + " (UTC+8/TPE)"
		embed = discord.Embed(
		title=race['raceName'],
		description=race['Circuit']['circuitName'],
		color=discord.Color.green()
		)
		embed.set_thumbnail(url=parseWikiImg(race['Circuit']['url']))
		embed.add_field(name='Season', value=race['season'], inline=True)
		embed.add_field(name='Round', value=race['round'], inline=True)
		embed.add_field(name='Location', value=loc, inline=True)
		embed.add_field(name='Time', value=dts, inline=True)
		await ctx.send(embed=embed)




@client.event
async def on_message(msg):
	#msg.content = msg.content.lower()
	if msg.author == client.user:
		return
	if not msg.content.startswith('!') and not ':thonk:' in msg.content and str(msg.author) == 'jc-hiroto#9838':
		for nm in cemojis:
			emoji = get(client.emojis, name=nm)
			# await msg.add_reaction(emoji)
	if ':thonk:' in msg.content:
		for nm in thonks:
			emoji = get(client.emojis, name=nm)
			await msg.add_reaction(emoji)
		#emoji = get(client.emojis, name='thonk')
		#await msg.add_reaction(emoji)
	if msg.content.startswith('那你很') or msg.content.startswith('那他很'):
		emoji = get(client.emojis, name='sucks')
		adj = msg.content
		await msg.add_reaction(emoji)
		async with msg.channel.typing():
			sleep(2)
		await msg.channel.send('對阿 '+adj)

	if "吃啥" in msg.content:
		askMsg = await msg.channel.send('需要建議ㄇ🧐')
		await askMsg.add_reaction('✅')
		def check(reaction, user):
			return str(reaction.emoji) in '✅' and reaction.message == askMsg and user != client.user
		try:
			checked = await client.wait_for('reaction_add', check=check, timeout=10)
			if checked:
				embed = randEat()
				await msg.channel.send('那就吃')
				async with msg.channel.typing():
					sleep(1)
				await msg.channel.send(embed=embed)
		except asyncio.exceptions.TimeoutError:
			await askMsg.delete()
	await client.process_commands(msg)

print('Bot Starting...')
client.run(config.DISCORD_BOT_TOKEN)
