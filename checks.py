async def is_admin(ctx):
    is_admin = ctx.bot.db.is_admin(ctx.author.id)
    if not is_admin:
        await ctx.message.add_reaction("❌")
    return is_admin
