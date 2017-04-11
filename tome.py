import asyncio
import discord
import json
import random
import operator
import re

#operator look up table for the diceroller
ops = {"+":operator.add,"-":operator.sub}

#edit these values if you want to load the various json files from different folders.
paths = {"license":"license.json","spells":"spells.json","monsters":"monsters.json","token":"token.json","log":"log.json"}

license = {}
with open(paths["license"],'r') as fp:
    license = json.load(fp)

spells = {}
with open(paths["spells"],'r') as fp:
    spells = json.load(fp)

monsters = {}
with open(paths["monsters"],'r') as fp:
    monsters = json.load(fp)

tokens = {}
with open(paths["token"],'r') as fp:
    tokens = json.load(fp)

log = {}
with open(paths["log"],'r') as fp:
    log = json.load(fp)

token = tokens['token']

class TomeBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.GamePlaying = discord.Game()
        self.GamePlaying.name = "Type ?commands"

    async def on_message(self, message):
        global log
        if message.content.startswith("?"):
            if len(log) > 9:
                log = log[-9:]
            try:
                messagelog = {"messageID":message.id,"userID":message.author.id,"username":message.author.name,"timestamp":str(message.timestamp),"content":message.content,"serverID":message.server.id,"servername":message.server.name,"channelID":message.channel.id,"channelname":message.channel.name,"privatemessage":False}
            except:
                messagelog = {"messageID":message.id,"userID":message.author.id,"username":message.author.name,"timestamp":str(message.timestamp),"content":message.content,"privatemessage":True}
            log.append(messagelog)
            with open(paths["log"],'w') as fp:
                json.dump(log, fp)
            command = (message.content.split(' ',1)[0])[1:]
            if hasattr(self, command):
                response = getattr(self, command)(message)
                if type(response) is list:
                    if response[0] != None:
                        for a in response:
                            await self.send_message(message.channel, a)
                else:
                    await self.send_message(message.channel,embed=response)


    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.change_presence(game=self.GamePlaying)

    def commands(self, message):
        if message.content.lower().endswith("-p"):
            response= """
Commands:
?roll - roll dice, syntax ?roll xdy
?spellsearch - search for a dnd 5e spell
?spellinfo - get information about a specific dnd 5e spell
?monstersearch - search for a dnd 5e monster
?monsterinfo - get information about a specific dnd 5e monster
suffixes: -p (plain) forces responses to be in plaintext without embeds.
"""
            return([response])
        else:
            response = discord.Embed()
            response.colour = discord.Colour.dark_purple()
            response.title = "Bot Commands"
            response.type = "rich"
            response.add_field(name="?roll",value="Rolls dice. Can add or subtract modifiers to individual dice or the total of the rolls.\n \"?roll xdy+z\" - adds modifier to each dice.\n \"?roll xdy +z\" - adds modifier to the total.",inline=False)
            response.add_field(name="?spellsearch",value="Searches for a 5e spell.\nNot case sensitive, and uses metadata to help you search.\nYou can search by class, level, name, components, range and more.\nSeperate search terms with commas.\n \"?spellsearch 1st, Bard, touch\" - searches for 1st level Bard spells with a range of touch.",inline=False)
            response.add_field(name="?spellinfo",value="Gives information about a spell.\nNot case sensitive, but does have to be spelt correctly.\n \"?spellinfo Cure Wounds\"",inline=False)
            response.add_field(name="?monstersearch",value="Same as spellsearch, but for 5e monsters\nAlso works with metadata such as size, challenge rating, etc.",inline=False)
            response.add_field(name="?monsterinfo",value="Same as spellinfo, but for 5e monsters.",inline=False)
            response.add_field(name="?info",value="Show information about the bot.",inline=False)
            response.add_field(name="suffixes",value="Use -p (stands for plain) to use a command without it returing an embed.\nFor those who have link embeds turned off in their discord settings.\n \"?commands -p\" displays this page in a non embed format.",inline=False)
            return(response)

    def info(self, message):
        inguilds = 0
        for sever in self.servers:
            inguilds = inguilds + 1
        response = """
Type ?commands to see the commands.
Add the suffix -p to disable embeds.
?commands -p

Find the owner of the Bot here:
https://discord.gg/25bf5NT

also on github:
https://github.com/Carbsta/TomeBot

Hosted by @Crablabuk.

To add to your server use this link:
https://discordapp.com/oauth2/authorize?client_id=247413966094073856&scope=bot&permissions=0
"""
        response = response +"\n\nCurrently in "+str(inguilds)+" discord server(s)."
        return([response])



    def roll(self, message):
        try:
            words = message.content.split(" ")
            dicenumbers = words[1].split("d")
            try:
                modifierint = words[2][1:]
                modifiersign = words[2][:1]
            except:
                modifierint = ""
                modifiersign = ""
            total = 0
            rolls = "Rolls are: "
            if len(dicenumbers[0]) < 4:
                for x in (range(0,int(dicenumbers[0]))):
                    if "+" in dicenumbers[1]:
                        values = dicenumbers[1].split("+")
                        roll = random.randint(1,int(values[0]))
                        rolls += str(roll)+"+"+values[1]
                        roll = roll + int(values[1])
                        rolls += "="+str(roll)+", "
                    elif "-" in dicenumbers[1]:
                        values = dicenumbers[1].split("-")
                        roll = random.randint(1,int(values[0]))
                        rolls += str(roll)+"-"+values[1]
                        roll = roll - int(values[1])
                        rolls += "="+str(roll)+", "
                    else:
                        roll = random.randint(1,int(dicenumbers[1]))
                        rolls += str(roll)+", "
                    total += roll
                if modifiersign == "":
                    rolls = rolls[:-2]+". Total = "+str(total)
                else:
                    rolls = rolls[:-2]+". "+modifiersign+" "+modifierint+". Total = "+str(ops[modifiersign](total,int(modifierint)))
                if len(rolls)>1900:
                    rolls = "Don't do stupid stuff with the Roll command."
            else:
                rolls = "Don't do stupid stuff with the Roll command."
        except:
            rolls = "Don't do stupid stuff with the Roll command."
        return([rolls])

    def spellinfo(self, message):
        noembed = False
        words = message.content
        if message.content.endswith("-p"):
            noembed = True
            words = words.strip(" -p")
            words = words.strip("-p")
        searchterm = words.split(' ',1)[1].lower()
        results = []
        result = "Could not find that spell, use ?spellsearch to get spell names."
        embedresult = discord.Embed()
        embedresult.type = "rich"
        embedresult.colour = discord.Colour.dark_purple()
        embedresult.add_field(name="No spell found",value="Use ?spellsearch to get spell names.",inline=False)
        for x in spells:
            if searchterm == x['name'].lower():
                result = x['name']+"\n\n"+x['level']+"\n\nDescription: \n"+x['desc']
                embedresult.clear_fields()
                embedresult.title = x['name']
                embedresult.add_field(name=x['level'],value="\u200b",inline=False)
                desc = x['desc']
                if(len(desc)<=1000):
                    embedresult.add_field(name="Description:",value=x["desc"],inline=False)
                else:
                    descarray = desc.split("\n")
                    for a in descarray:
                        if re.search('[a-zA-Z]', a):
                            if(descarray.index(a)==0):
                                if (len(a)<1000):
                                    embedresult.add_field(name="Description:",value=a,inline=False)
                            else:
                                if (len(a)<1000):
                                    embedresult.add_field(name="\u200b",value=a,inline=False)
                
                try:
                    result = result + "\n" + x['higher_level']
                    embedresult.add_field(name="Higher Levels:",value=x['higher_level'],inline=False)
                except:
                    result = result
                    embedresult = embedresult
                result = result + "\nCasting time: "+x['casting_time']+"\nDuration: "+x['duration']+"\nRange: "+x['range']
                result = result + "\n\nConcentration: "+x['concentration']+"\nRitual: "+x['ritual']+"\n\nComponents: "+x['components']
                embedresult.add_field(name="Casting time:",value=x['casting_time'],inline=False)
                embedresult.add_field(name="Duration:",value=x['duration'],inline=False)
                embedresult.add_field(name="Range:",value=x['range'],inline=False)
                embedresult.add_field(name="Concentration:",value=x['concentration'],inline=False)
                embedresult.add_field(name="Ritual:",value=x['ritual'],inline=False)
                embedresult.add_field(name="Components:",value=x['components'],inline=False)
                try:
                    result = result + "\nMaterials: "+x['material']
                    embedresult.add_field(name="Materials:",value=x['material'],inline=False)
                except:
                    result = result
                    embedresult = embedresult
                result = result + "\n\nClass: "+x['class']
                embedresult.add_field(name="Class:",value=x['class'],inline=False)
        results = [result]
        if (len(result)>=2000):
            correctLength = False
            results = []
            while correctLength == False:
                item = result[0:2000]
                results.append(item)
                result = result[2000:]
                if len(result) <= 2000:
                    correctLength = True
                    item = result
                    results.append(item)

        if noembed == False:
            return(embedresult)
        else:
            return(results)

    def spellsearch(self, message):
        words = message.content
        if words.endswith("-p"):
            words = words[:-2]
        searchterms = words.split(' ',1)[1].lower()
        searchterms = searchterms.split(", ")
        results = "Results: \n"
        for spell in spells:
            matches = 0
            for term in searchterms:
                if term in spell['name'].lower():
                    matches = matches + 1
                elif term in spell['class'].lower():
                    matches = matches + 1
                elif term in spell['school'].lower():
                    matches = matches + 1
                elif term in spell['level'].lower():
                    matches = matches + 1
                elif term in spell['duration'].lower():
                    matches = matches + 1
                elif term in spell['range'].lower():
                    matches = matches + 1
                elif ", M" in spell["components"]:
                    if term in spell["material"]:
                        matches = matches + 1
            if matches == len(searchterms):
                results = results+spell['name']+"\n"
        if len(results)>1990:
            results = "Too many results found, try narrowing your search with more search terms."
        return([results])

    def monstersearch(self,message):
        searchterm = message.content.split(' ',1)[1].lower()
        searchterm = searchterm.split(", ")
        results = "Results: \n"
        for monster in monsters:
            matches = 0
            for term in searchterm:
                if term in monster['name'].lower():
                    matches = matches + 1
                elif term in monster['size'].lower():
                    matches = matches + 1
                elif term in monster['type'].lower():
                    matches = matches + 1
                elif term in monster['subtype'].lower():
                    matches = matches + 1
                elif term in monster['alignment'].lower():
                    matches = matches + 1
                elif term in monster['senses'].lower():
                    matches = matches + 1
                elif term in monster['languages'].lower():
                    matches = matches + 1
            if matches == len(searchterm):
                results = results+monster['name']+"\n"
        if len(results)>1990:
            results = "Too many results found, try narrowing your search with more search terms."
        return([results])
        
    def deprecated(self,message):
        searchterm = message.content.split(' ',1)[1].lower()
        result = "Could not find that monster, use ?monstersearch to get monster names."
        abilities = "No special abilities"
        actions = "No actions"
        legendaryactions = "No legendary actions"
        for x in monsters:
            if searchterm == x['name'].lower():
                result = "**"+x['name']+"**\n\n"+"Size: "+x['size']+"\nChallenge Rating: "+x['challenge_rating']+"\nType: "+x['type']
                if x['subtype'] != "":
                    result = result + "\nSubtype: "+x['subtype']
                result = result +"\nAlignment: "+x['alignment']+"\nSenses: "+x['senses']+"\nLanguages: "+x['languages']
                try:
                    abilities = "**Special abilities:**\n\n"
                    for y in x['special_abilities']:
                        abilities = abilities + y['name']+"\n"+y['desc']+"\n\n"
                except:
                    abilities = "No special abilities"
                try:
                    actions = "**Actions:**\n\n"
                    for z in x['actions']:
                        actions = actions + z['name']+"\n"+z['desc']+"\n\n"
                except:
                    actions = "No actions"
                try:
                    legendaryactions = "**Legendary Actions:**\n\n"
                    for w in x['legendary_actions']:
                        legendaryactions = legendaryactions + w['name']+"\n"+w['desc']+"\n\n"
                except:
                    legendaryactions = "No legendary actions"
                result = result + "\n\n**For DM specific info such as Stats, armor class etc, use ?dminfo instead**"
        results = [result,abilities,actions,legendaryactions]
        for b in results:
            if len(b)>1900:
                firstpart, secondpart = b[:len(b)//2], b[len(b)//2:]
                index = results.index(b)
                results.remove(b)
                results.insert(index,secondpart)
                results.insert(index,firstpart)

        return(results)

    def dminfo(self,message):
        response = "dminfo is now deprecated, ?monsterinfo now displays everything dminfo used to display."
        return([response])

    def monsterinfo(self,message):
        noembed = False
        searchterm = message.content.split(' ',1)[1].lower()
        if message.content.endswith("-p"):
            noembed = True
            searchterm = searchterm.strip(" -p")
            searchterm = searchterm.strip("-p")
        result = "Could not find that monster, use ?monstersearch to get monster names."
        stats = "No stats"
        abilities = "No special abilities"
        actions = "No actions"
        legendaryactions = "No legendary actions"
        embedresult = discord.Embed()
        embedresult.type = "rich"
        embedresult.colour = discord.Colour.dark_purple()
        embedresult.add_field(name="No monster found",value="Use ?monstersearch to get monster names.",inline=False)
        for x in monsters:
            if searchterm == x['name'].lower():
                #generate name and info fields
                embedresult.clear_fields()
                resulttitle = "**"+x['name']+"**\n\n"
                result = "Size: "+x['size']+"\nChallenge Rating: "+x['challenge_rating']+"\nType: "+x['type']
                if x['subtype'] != "":
                    result = result + "\nSubtype: "+x['subtype']
                result = result +"\nAlignment: "+x['alignment']+"\nSenses: "+x['senses']+"\nLanguages: "+x['languages']
                embedresult.add_field(name=x['name'],value=result,inline=False)
                result = resulttitle + result

                #generate stat fields
                statstitle = "**Stats:**\n\n"
                stats = "Armor class: "+str(x['armor_class'])+"\nHit points: "+str(x['hit_points'])+"\nHit dice: "+x['hit_dice']
                stats = stats+"\n\nSpeed: "+x['speed']+"\n\nStrength: "+str(x['strength'])+"\nDexterity: "+str(x['dexterity'])
                stats = stats+"\nConstitution: "+str(x['constitution'])+"\nIntelligence: "+str(x['intelligence'])+"\nWisdom: "+str(x['wisdom'])
                stats = stats+"\nCharisma: "+str(x['charisma'])+"\n"

                #getting all the random shit crazy stats that are different for each monster -.-"
                skills = ["Acrobatics","Arcana","Athletics","Deception","History","Insight","Intimidation","Investigation","Medicine","Nature","Perception","Performance","Persuasion","Religion","Stealth","Survival"]
                savingthrows = ["Strength_save","Dexterity_save","Constitution_save","Intelligence_save","Wisdom_save","Charisma_save"]
                resistances = ["Damage_vulnerabilities","Damage_resistances","Damage_immunities","Condition_immunities"]

                for skill in skills:
                    stat = x.get(skill.lower())
                    if stat != None:
                        stats = stats + skill +": "+str(stat)+"\n"
                stats = stats+"\n"

                for save in savingthrows:
                    stat = x.get(save.lower())
                    if stat != None:
                        stats = stats + save +": "+str(stat)+"\n"
                stats = stats+"\n"

                for resistance in resistances:
                    stat = x.get(resistance.lower())
                    if stat != "":
                        stats = stats + resistance +": "+stat+"\n"
                embedresult.add_field(name="Stats:",value=stats,inline=False)
                stats = statstitle + stats

                #special abilites, actions and legendary actions.
                try:
                    abilitiestitle = "**Special abilities:**\n\n"
                    abilities = ""
                    for y in x['special_abilities']:
                        abilities = abilities + y['name']+"\n"+y['desc']+"\nAttack bonus: "+str(y['attack_bonus'])+"\n\n"
                except:
                    abilitiestitle = ""
                    abilities = "No special abilities."
                if (len(abilities)<1000):
                    embedresult.add_field(name="Special Abilities:",value=abilities,inline=False)
                abilities = abilitiestitle + abilities
                try:
                    actionstitle = "**Actions:**\n\n"
                    actions = ""
                    for z in x['actions']:
                        actions = actions + z['name']+"\n"+z['desc']+"\nAttack bonus: "+str(z['attack_bonus'])
                        try:
                            actions = actions + "\nDamage dice: "+z['damage_dice']
                        except:
                            actions = actions
                        try:
                            actions = actions + "\nDamage bonus: "+z['damage_bonus']+"\n\n"
                        except:
                            actions = actions
                        actions = actions + "\n\n"
                except:
                    actionstitle = ""
                    actions = "No actions"
                if (len(actions)<=1000):
                    embedresult.add_field(name="Actions:",value=actions,inline=False)
                else:
                    embedactionsarray = actions.split("\n\n")
                    for a in embedactionsarray:
                        if re.search('[a-zA-Z]', a):
                            if(embedactionsarray.index(a)==0):
                                if (len(a)<1000):
                                    embedresult.add_field(name="Actions:",value=a,inline=False)
                            else:
                                if (len(a)<1000):
                                    embedresult.add_field(name="\u200b",value=a,inline=False)
                actions = actionstitle + actions

                try:
                    legendaryactionstitle = "**Legendary Actions:**\n\n"
                    legendaryactions = ""
                    for w in x['legendary_actions']:
                        legendaryactions = legendaryactions + w['name']+"\n"+w['desc']+"\nAttack bonus: "+str(w['attack_bonus'])
                        try:
                            legendaryactions = legendaryactions + "\nDamage dice: "+w['damage_dice']
                        except:
                            legendaryactions = legendaryactions
                        try:
                            legendaryactions = legendaryactions + "\nDamage bonus: "+w['damage_bonus']+"\n\n"
                        except:
                            legendaryactions = legendaryactions
                        legendaryactions = legendaryactions + "\n\n"
                except:
                    legendaryactionstitle = ""
                    legendaryactions = "No legendary actions"
                if (len(legendaryactions)<1000):
                    embedresult.add_field(name="Legendary Actions:",value=legendaryactions,inline=False)
                legendaryactions = legendaryactionstitle + legendaryactions

        if noembed == False:
            return(embedresult)

        results = [result,stats,abilities,actions,legendaryactions]
        if (result == "Could not find that monster, use ?monstersearch to get monster names."):
            results = [result]
        for b in results:
            if len(b)>1900:
                firstpart, secondpart = b[:len(b)//2], b[len(b)//2:]
                index = results.index(b)
                results.remove(b)
                results.insert(index,secondpart)
                results.insert(index,firstpart)
        return(results)

bot = TomeBot()
bot.run(token)