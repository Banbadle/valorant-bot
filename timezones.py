import pytz
from discord.ext import commands
from discord.ui import Select, View
from discord import SelectOption

class Timezones(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Timezones.py loaded")
        
    @commands.command(help = "View and change your timezone.\n"+\
                      "parameters:\n    country: the country or region you are located")
    async def timezone(self, ctx, *country):
        '''View and change your timezone'''
        country = " ".join(country)
        if country=="":
            curr_tz = self.client.db.get_timezone(ctx.author)
            await ctx.author.send(f"Your current timezone is set to '{curr_tz}'.\nTo change this, type '?timezone ' followed by your country / region.\nExamples: '?timezone UK', ?'timezone Germany'")
        else:
            await self.send_country_shortlist(ctx, country)

    async def send_country_shortlist(self, ctx, country_query):
        select_menu = self.SelectCountry(self.client, country_query)
        if select_menu.options == []:
            return await ctx.author.send(f"I couldn't find any country called '{country_query}'. It's possible that this is named something else in my files. Please try again.")
        view = View()
        view.add_item(select_menu)
        await ctx.author.send("I found some results containing that.\nPlease select your country / region.", view=view)

    class SelectCountry(Select):
        
        def __init__(self, client, country_query):
            self.client = client
            
            option_list = []
            for _, check_country in pytz.country_names.items():
                if country_query.lower() in check_country.lower():
                    new_option = SelectOption(label=check_country, value=check_country)
                    option_list.append(new_option)
                    
            option_list = option_list[0:25]
            super().__init__(placeholder="Select a Country/Region", min_values=1, max_values=1, options=option_list)

        async def callback(self, interaction):
            await interaction.message.delete()
            await self.send_city_shortlist(interaction, self.values[0])
            
        async def send_city_shortlist(self, interaction, country):
            select_menu = Timezones.SelectCity(self.client, country)
            view = View()
            view.add_item(select_menu)
            return await interaction.response.send_message(content="Select the city which follows your timezone.", view=view, ephemeral=True)
            
    class SelectCity(Select):
        
        def __init__(self, client, country):
            self.client = client
            
            for code, check_country in pytz.country_names.items():
                if check_country.lower() == country.lower():
                    option_list = []
                    for city in pytz.country_timezones[code]:
                        new_option = SelectOption(label=city, value=city)
                        option_list.append(new_option)

                    option_list = option_list[0:25]
                    super().__init__(placeholder="Select a City", min_values=1, max_values=1, options=option_list)
                    
        async def callback(self, interaction):
            tz = self.values[0]
            self.client.db.set_timezone(interaction.user, tz)
            await interaction.response.send_message(content=f"You have changed your timezone to {tz}", ephemeral=True)

 
async def setup(client):
    await client.add_cog(Timezones(client))