import pytz
from discord.ext import commands
from discord_components import Select, Button, ButtonStyle, SelectOption, Interaction

# region_list = ['Africa',
#  'America',
#  'Antarctica',
#  'Arctic',
#  'Asia',
#  'Atlantic',
#  'Australia',
#  'Europe',
#  'Indian',
#  'Pacific']

class Timezones(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Timezones.py loaded")
        
    # def get_regions(self):
    #     return region_list
        
    # def get_countries_from_region(self, region):
    #     country_code_list = []
    #     for code, tz_list in pytz.country_timezones.items():
    #         if region.lower() == tz_list[0][0: len(region)].lower():
    #             country_code_list.append(code)
        
    #     country_list = sorted([country for code, country in pytz.country_names.items() if code in country_code_list])
    #     return country_list
    
    # def get_cities_from_country(self, country):
    #     for code, check_country in pytz.country_names.items():
    #         if check_country == country:
                
    #             tz_list = pytz.country_timezones[code]
    #             city_list = []
    #             for tz in tz_list:
    #                 _, city = tz.split("/",1)
    #                 city_list.append(city)
                    
    #             return sorted(city_list)
    #     return []
        
    @commands.command()
    async def timezone(self, ctx, country=""):
        if country=="":
            curr_tz = self.client.db.get_timezone(ctx.author.id)
            #change_button = Button(label="Change Timezone", style=ButtonStyle(3), custom_id="change_timezone")
            await ctx.author.send(f"Your current timezone is set to '{curr_tz}'.\nTo change this, type '?timezone ' followed by your country / region.\nExamples: '?timezone UK', ?'timezone Germany'")
        else:
            contain_list = []
            for code, check_country in pytz.country_names.items():
                if check_country.lower() == country.lower():
                    return await self.send_city_shortlist(ctx, check_country)
                
                if country.lower() in check_country.lower():
                    contain_list.append(check_country)
            
            if contain_list != []:
                if len(contain_list) < 25:
                    return await self.send_country_shortlist(ctx, contain_list)
                else:
                    return await ctx.author.send(f"There were too many results containing '{country}'. Please try again")
            
            return await ctx.author.send(f"I couldn't find any country called '{country}'. It's possible that this is named something else in my files. Please try again.")
            
    async def send_country_shortlist(self, ctx, country_list):
        option_list = []
        for country in country_list:
            new_option = SelectOption(label=country, value=f"tz_country_{country}")
            option_list.append(new_option)
        
        return await ctx.author.send("This has returned multiple choices. Please select your country / region.", components=[Select(placeholder="Select Country/Region", options=option_list)])
    
    async def send_city_shortlist(self, ctx, country):
        for code , check_country in pytz.country_names.items():
            if check_country.lower() == country.lower():
                option_list = []
                for city in pytz.country_timezones[code]:
                    new_option = SelectOption(label=city, value=f"tz_final_{city}")
                    option_list.append(new_option)
                    
                return await ctx.channel.send(content="Select the city which follows your timezone.", components=[Select(placeholder="Select City", max_values=1, options=option_list)])
                    
        return await ctx.respond(content="Something went wrong, sorry. I have no idea what")
        
    # @commands.Cog.listener()
    # async def on_button_click(self, interaction):
    #     if interaction.custom_id == "change_timezone":
    #         option_list = []
    #         for region in region_list:
    #             new_option = SelectOption(label=region, value=f"tz_region_{region}")
    #             option_list.append(new_option)
    #         await interaction.send(content="Select a Region", components=[Select(placeholder="Region", max_values=1, options=option_list)])
            
    @commands.Cog.listener()
    async def on_select_option(self, interaction):
   
        PREFIX_COUNTRY = "tz_country"     
        if interaction.values[0][0:len(PREFIX_COUNTRY)] == PREFIX_COUNTRY:
            _,_,country = interaction.values[0].split("_")
            await self.send_city_shortlist(interaction, country)
            await interaction.message.delete()
            return
    
        PREFIX_FINAL = "tz_final"
        if interaction.values[0][0:len(PREFIX_FINAL)] == PREFIX_FINAL:
            _,_,tz = interaction.values[0].split("_")
            self.client.db.set_timezone(interaction.user.id, tz)
            await interaction.send(content=f"You have changed your timezone to {tz}", ephemeral=False)
            await interaction.message.delete()
            return
           
        # PREFIX_REGION = "tz_region"
        # if interaction.values[0][0:len(PREFIX_REGION)] == PREFIX_REGION:
        #     _,_, region = interaction.values[0].split("_")
        #     country_list = self.get_countries_from_region(region)
        #     option_list = []
        #     for country in country_list:
        #         new_option = SelectOption(label=country, value=f"tz_country_{country}_{region}")
        #         option_list.append(new_option)
        #     await interaction.respond(content="Select a Country", components=[Select(placeholder="Country", max_values=1, options=option_list)])
            
        # PREFIX_COUNTRY = "tz_country"
        # if interaction.values[0][0:len(PREFIX_COUNTRY)] == PREFIX_COUNTRY:
        #     _,_,country,region = interaction.values[0].split("_")
        #     city_list = self.get_cities_from_country(country)
        #     option_list = []
        #     for city in city_list:
        #         new_option  = SelectOption(label=city, value=f"tz_city_{city}_{region}")
        #         option_list.append(new_option)
        #     await interaction.respond(content="Select a City", components=[Select(placeholder="City", max_values=1, options=option_list)])
            
        # PREFIX_CITY = "tz_city"
        # if interaction.values[0][0:len(PREFIX_CITY)] == PREFIX_CITY:
        #     _,_, city, region = interaction.values[0].split("_")
        #     new_tz = f"{region}/{city}"
        #     await interaction.respond(f"Your timezone is now {new_tz}")
            
    
def setup(client):
    client.add_cog(Timezones(client))