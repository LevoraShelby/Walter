import json
import random
import asyncio
from typing import List
import discord
from jproperties import Properties
import os
import re


def parseProps(props):
	return {
		'brettIds': parseNumList(props['brettIds'].data),
		'casIds': parseNumList(props['casIds'].data),
		'trevorId': int(props['trevorId'].data),
		'serverIds': parseNumList(props['serverIds'].data),
		'walterEmoji': props['walterEmoji'].data,
		'botToken': props['botToken'].data,
		'botConfigFp': props['botConfigFp'].data,
	}

def parseNumList(s: str) -> List[int]:
	return [int(num) for num in s.split(',')]

props = Properties()
env = os.environ['WALTER_ENV']
with open(f'{env}.properties', 'rb') as propFile:
	props.load(propFile)
pprops = parseProps(props)

def readBotConfig():
	return json.load(open(pprops['botConfigFp']))

def setChance(chance):
	configFile = open(pprops['botConfigFp'])
	config = json.load(configFile)
	config['chance'] = chance
	json.dump(config, open(pprops['botConfigFp'], 'w'))


intents = discord.Intents.default()
intents.message_content=True

botClient = discord.Client(intents=intents)

@botClient.event
async def on_message(message: discord.Message):
	isBrett = message.author.id in pprops['brettIds']
	inGuild = message.channel.type == discord.ChannelType.text and message.guild.id in pprops['serverIds']
	isCas = message.author.id in pprops['casIds']
	inDm = message.channel.type == discord.ChannelType.private
	isRelay = message.content.startswith('relay ')
	if inDm:
		print(message.content)
	
	if isBrett and inGuild:
		chance = readBotConfig()['chance']
		await message.add_reaction('<:1892walter:1012486290085773323>')
		toWalter = random.choices([True, False], [chance, 100 - chance])[0]
		if toWalter:
			await message.channel.send('<:1892walter:1012486290085773323>')
	elif message.author.id == pprops['trevorId'] and isRelay:
		await botClient.get_channel(913514415628902432).typing()
		await asyncio.sleep(min((len(message.content) / 10), 5))
		await botClient.get_channel(913514415628902432).send(''.join(message.content.split('relay ')))
	elif isCas and inDm:
		if re.search('^\d+(\.\d+)?$', message.content):
			setChance(float(message.content))
			await message.channel.send('Walter!')
		else:
			await message.channel.send('Walter?')


botClient.run(pprops['botToken'])
