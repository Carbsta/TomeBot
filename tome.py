import asyncio
import discord
import json
import random
import operator

#operator look up table for the diceroller
ops = {"+":operator.add,"-":operator.sub}

license = {}
with open('license.json','r') as fp:
    license = json.load(fp)

spells = {}
with open('spells.json','r') as fp:
    spells = json.load(fp)

monsters = {}
with open('monsters.json','r') as fp:
    monsters = json.load(fp)

tokens = {}
with open('token.json','r') as fp:
    tokens = json.load(fp)

token = tokens['token']

class TomeBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.GamePlaying = discord.Game()
        self.GamePlaying.name = "Type ?commands"

    async def on_message(self, message):
        output = ""
        try:
            output = output + message.server.name + " - " + message.channel.name + " - "
        except:
            output = output + "Private Message - "
        output = output + message.author.name + " (" + str(message.timestamp) + ") :\n" + message.content
        print(output)
        if message.content.startswith("?"):
            command = (message.content.split(' ',1)[0])[1:]
            if hasattr(self, command):
                response = getattr(self, command)(message)
                if response[0] != None:
                    for a in response:
                        await self.send_message(message.channel, a)


    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.change_status(self.GamePlaying, idle = False)

    def commands(self, message):
        response= """Commands:
        ?roll - roll dice, syntax ?roll xdy
        ?spellsearch - search for a dnd 5e spell
        ?spellinfo - get information about a specific dnd 5e spell
        ?monstersearch - search for a dnd 5e monster
        ?monsterinfo - get information about a specific dnd 5e monster
        ?dminfo - like monsterinfo, but also gives stats such as armor class, hp etc.

        To find this bot in its main server (which it was built for) join here:
        https://discord.gg/25bf5NT

        also on github too!
        https://github.com/Carbsta/TomeBot
        If you want to help me implement Volo's, or work on the SRD version come find me here.

        To add to your server use this link:
        https://discordapp.com/oauth2/authorize?client_id=247413966094073856&scope=bot&permissions=0
        (it doesn't require any permisions and never will)
        """
        return([response])


    def roll(self, message):
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
            

    def spellinfo(self, message):
        searchterm = message.content.split(' ',1)[1].lower()
        results = []
        result = "Could not find that spell, use ?spellsearch to get spell names."
        for x in spells:
            if searchterm == x['name'].lower():
                result = x['name']+"\n\n"+x['level']+"\n\nDescription: \n"+x['desc']
                try:
                    result = result + "\n" + x['higher_level']
                except:
                    result = result
                result = result + "\nCasting time: "+x['casting_time']+"\nDuration: "+x['duration']+"\nRange: "+x['range']
                result = result + "\n\nConcentration: "+x['concentration']+"\nRitual: "+x['ritual']+"\n\nComponents: "+x['components']
                try:
                    result = result + "\nMaterials: "+x['material']
                except:
                    result = result
                result = result + "\n\nClass: "+x['class']
        results = [result]
        if len(result)>1999:
            firstpart, secondpart = result[:len(result)//2], result[len(result)//2:]
            results = [firstpart,secondpart]

        return(results)

    def spellsearch(self, message):
        searchterm = message.content.split(' ',1)[1].lower()
        results = "Results: \n"
        for x in spells:
            if searchterm in x['name'].lower():
                results = results+x['name']+"\n"
        return([results])

    def monstersearch(self,message):
        searchterm = message.content.split(' ',1)[1].lower()
        results = "Results: \n"
        for x in monsters:
            if searchterm in x['name'].lower():
                results = results+x['name']+"\n"
        return([results])

    def monsterinfo(self,message):
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
        searchterm = message.content.split(' ',1)[1].lower()
        result = "Could not find that monster, use ?monstersearch to get monster names."
        stats = "No stats"
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
                        abilities = abilities + y['name']+"\n"+y['desc']+"\nAttack bonus: "+str(y['attack_bonus'])+"\n\n"
                except:
                    abilities = "No special abilities"
                try:
                    actions = "**Actions:**\n\n"
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
                    actions = "No actions"
                try:
                    legendaryactions = "**Legendary Actions:**\n\n"
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
                    legendaryactions = "No legendary actions"

                stats = "**Stats:**\n\n"+"Armor class: "+str(x['armor_class'])+"\nHit points: "+str(x['hit_points'])+"\nHit dice: "+x['hit_dice']
                stats = stats+"\n\nSpeed: "+x['speed']+"\n\nStrength: "+str(x['strength'])+"\nDexterity: "+str(x['dexterity'])
                stats = stats+"\nConstitution: "+str(x['constitution'])+"\nIntelligence: "+str(x['intelligence'])+"\nWisdom: "+str(x['wisdom'])
                stats = stats+"\nCharisma: "+str(x['charisma'])+"\n\n"

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

        results = [result,stats,abilities,actions,legendaryactions]
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