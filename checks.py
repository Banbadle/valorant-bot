async def is_admin(ctx):
    return ctx.bot.db.is_admin(ctx.author.id)
