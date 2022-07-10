
from nltk.probability import FreqDist
import tools

######################################################################################################################

# Simplified Message model
# Pickleable, contains frequency distribution of normalised text

class Message:
    __author = None # string
    __text = None # string
    __guild_id = None # integer
    __channel_id = None # integer
    __message_id = None # integer 
    __attachments = None # list of strings (URLs)
    __hashid = None # string
    __freqdist = None # FreqDist from NLTK package
    # for word in __freqdist - iteration over all words
    # __freqdist[word] = number of occurances in text
    def __init__(self, author, text, guild_id, channel_id, message_id, attachments):
        self.__author = author
        self.__text = text
        self.__guild_id = guild_id
        self.__channel_id = channel_id
        self.__message_id = message_id
        self.__attachments = attachments
        self.__hashid = Message.CalculateHash(guild_id, channel_id, message_id)
        self.__freqdist = FreqDist( tools.english_normalisation(text).split() )
    def ConvertDiscordMessage(dc_message):
        author = dc_message.author.name
        guild_id = dc_message.guild.id
        channel_id = dc_message.channel.id
        message_id = dc_message.id
        text = dc_message.content
        attachments =  [ attachment.url for attachment in dc_message.attachments ]
        return Message(author, text, guild_id, channel_id, message_id, attachments)
    def CalculateHash(guild_id, channel_id, message_id):
        return tools.Hash(str(guild_id) + str(channel_id) + str(message_id))
    
    def Author(self):
        return self.__author
    def Text(self):
        return self.__text
    def GuildId(self):
        return self.__guild_id
    def ChannelId(self):
        return self.__channel_id
    def MessageId(self):
        return self.__message_id
    def Attachments(self):
        return self.__attachments
        
    def Link(self):
        return tools.link_to_message(self.GuildId(), self.ChannelId(), self.MessageId())
    def HashId(self):
        return self.__hashid
    def FreqDist(self):
        return self.__freqdist
    def __str__(self):
        header = tools.wrap_bold(f"Written by: {self.Author()}")
        link = f"Link: {self.Link()}"
        return f"{header}\n{link}\n{self.Text()}"
        
######################################################################################################################

# debugging code

import triggers

async def on_message(local_env, message, normalised_text):
    pass
    #m = Message.ConvertDiscordMessage(message)
    #print(m)
triggers.on_message.append(on_message)