import json, re
from urllib.request import urlopen as GET
from urllib.error import HTTPError
from os import path

from discord.ext.commands import Cog
from discord import Embed

from apscheduler.triggers.cron import CronTrigger
from datetime import date

with open(path.join(path.dirname(path.dirname(__file__)), "config.json")) as f:
    guild_id = json.load(f)['base']['guild_id']


class YT_Upload(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lastVideoId = None
        self.youtube_apiKey = ""
        self.youtube_channelId = "UC6sb0bkXREewXp2AkSOsOqg"
        self.youtube_baseUrl = "https://youtube.googleapis.com/youtube/v3/search?part=snippet&channelId={channelId}&maxResults={count}&order=date&type=video&key={apiKey}"
        self.youtube_videoBaseUrl = "https://youtu.be/{videoId}"
        self.youtube_channelBaseUrl = f"https://youtube.com/channel/{self.youtube_channelId}"
        self.youtube_thumbnailBaseUrl = "https://i.ytimg.com/vi/{videoId}/hqdefault.jpg"

    def link_fix(self, desc):
      pattern = r'(https?://[A-Z,a-z,0-9]+\.[A-Z,a-z0-9]+[^\s]*)'
      maxLen = 100 #default length

      #sanity check
      num = len(re.findall(pattern, desc))
      if (num <= 0):
        return maxLen
      if (len(desc) <= maxLen):
        return maxLen

      parts = re.split(pattern, desc)
      #loop though every found url and check if it is positioned right at the 'maxLen' character border
      for i in range(len(parts)):
        if (re.search(pattern, parts[i])):
          start = len(''.join(parts[:i]))
          end = start+len(parts[i])
          if(start < maxLen and end >= maxLen):
            #found a url at the border - extend maxLen to end of url (plus 3 because of '...' at the end)
            return end+3

      #otherwise keep maxLen
      return maxLen

    def format_description(self, desc, maxLen):
      embedDesc = None
      #sanity check
      if (desc == None or len(desc) <= 0):
        return embedDesc

      #search for prefix in description
      ## NOTE: This part doesn't work, because yt api does not give line-breaks in the description >:(
      # prefix = "[BOT] "
      # paragraphs = desc.split('\n')
      # for p in paragraphs:
      #   if (p.startswith(prefix)):
      #     embedDesc = p[len(prefix):]
      #     break

      # #if no prefix was found, take the first paragraph
      # if (embedDesc == None):
      #   embedDesc = paragraphs[0]

      ## NOTE: The following line is a workaround, remove it and uncomment (and fix it?) the obove section when linebreaks are detectable
      embedDesc = desc

      #limit num of characters
      if (len(embedDesc) > maxLen):
        embedDesc = embedDesc[:maxLen-3] + "..."

      return embedDesc

    async def announceVideo(self, video):
        self.lastVideoId = video['id']['videoId']
        videoTitle = video['snippet']['title']
        videoDescription = video['snippet']['description']
        channelTitle = video['snippet']['channelTitle']

        newVideoEmbed = Embed(
            title=videoTitle,
            url=self.youtube_videoBaseUrl.format(videoId=self.lastVideoId),
            description=self.format_description(videoDescription, self.link_fix(videoDescription)),
            color=0xff0000)
        newVideoEmbed.set_author(
            name=f"{channelTitle} hat ein Neues Video hochgeladen!")
        newVideoEmbed.set_image(
            url=self.youtube_thumbnailBaseUrl.format(videoId=self.lastVideoId))
        newVideoEmbed.set_footer(
            text=f"{self.bot.user.display_name} > YouTube-Glocke",
            icon_url=self.bot.user.avatar_url)

        await self.bot.yt_notify.send(embed=newVideoEmbed)

    async def checkVideo(self):
        try: #get newest Video
            with GET(self.youtube_baseUrl.format(
                channelId=self.youtube_channelId,
                count=1,
                apiKey=self.youtube_apiKey,
            )) as f:
                video = json.load(f)['items'][0]
        except (HTTPError) as e:
            self.bot.log.warn(f"catched request error: {e}")
            return

        skipFirst = True
        if(self.lastVideoId == None and skipFirst):
            self.lastVideoId = video['id']['videoId']
            self.bot.log.info(f"[YouTube-Upload] lastVideoId was empty. Saved new id ({self.lastVideoId}) and skip posting to avoid doubble posting.")
            return
        elif(self.lastVideoId == video['id']['videoId']):
            self.bot.log.debug("[YouTube-Upload] lastVideoId same as new video ID. Not sent to avoid doubble posting.")
            return

        await self.announceVideo(video)

    @Cog.listener()
    async def on_ready(self):
        with open(path.join(path.dirname(path.dirname(__file__)), "lib/youtube_apiKey.0"), "r", encoding="utf-8") as f:
            self.youtube_apiKey = f.read()[:-1]

        self.bot.scheduler.add_job(self.checkVideo, CronTrigger(
            minute='*/15'), misfire_grace_time=40)

        self.bot.cogs_ready.ready_up(path.basename(__file__)[:-3])

def setup(bot):
    if bot.debug:
        return  # yt module not loaded in debug mode
    bot.add_cog(YT_Upload(bot))
