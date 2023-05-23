from discord import Interaction

async def is_admin(ctx):
    return ctx.bot.db.is_admin(ctx.author.id)

def slash_is_admin(interaction: Interaction):
    return interaction.client.db.is_admin(interaction.user.id)