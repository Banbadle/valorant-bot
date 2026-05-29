import discord
from discord.ext import commands
import random
from checks import is_admin
import asyncio


# ---------------------------------------------------------------------------
# Tournament constants
# ---------------------------------------------------------------------------

ACTIVE_COLOUR = 0x30cc74            # Poggies-this-is-my-current-team green
START_PRIZE   = 80                  # Payout if a user is supreme overlord

TOURNAMENT_NAME = "2026 World Cup"

class Round:
    # name: display name
    # loss_colour: colour applied to teams eliminated in this round
    # join_winner_prize: payout if a user's LATEST loss colour is this round's
    #                    AND their current (active) team eventually wins
    # reassign_after: True -> addresult moves loser's users to the winner.
    #                 False for group stage (handled separately) and final.
    def __init__(self, name, loss_colour, join_winner_prize, reassign_after):
        self.name = name
        self.loss_colour = loss_colour
        self.join_winner_prize = join_winner_prize
        self.reassign_after = reassign_after


# Listed in chronological elimination order. A user's "join tier" is the index of
# their LATEST loss-colour role (when they were last reassigned to a new team).
# Group Stage reassignment is handled by postgroupstagereassignment (random pairing),
# not addresult, so reassign_after is False there (technically doesn't matter)
ROUNDS = [
    Round("Group Stage",   0xd60f0f, 40, reassign_after=False),
    Round("Round of 32",   0xec1c68, 50, reassign_after=True),
    Round("Round of 16",   0xd67676, 30, reassign_after=True),
    Round("Quarter Final", 0xff5018, 20, reassign_after=True),
    Round("Semi Final",    0xfcad00, 10, reassign_after=True),
    Round("Final",         0xbfe57c,  0, reassign_after=False),
]

ROUND_ALIASES = {
    "groups":       "Group Stage",  "groupstage":  "Group Stage",
    "g":            "Group Stage",  "gs":          "Group Stage",
    "r32":          "Round of 32",  "round32":     "Round of 32",
    "roundof32":    "Round of 32",  "32":          "Round of 32",
    "r16":          "Round of 16",  "round16":     "Round of 16",
    "roundof16":    "Round of 16",  "16":          "Round of 16",
    "qf":           "Quarter Final","quarter":     "Quarter Final",
    "quarterfinal": "Quarter Final","quarterfinals":"Quarter Final",
    "sf":           "Semi Final",   "semi":        "Semi Final",
    "semifinal":    "Semi Final",   "semifinals":  "Semi Final",
    "f":            "Final",        "final":       "Final",
}


# ---------------------------------------------------------------------------
# Countries (2026 World Cup, 48 teams)
# ---------------------------------------------------------------------------

COUNTRIES = {
    # CONCACAF (6)
    "Canada":                 {"flag": ":flag_ca:", "demonym": "Canadian"},
    "Mexico":                 {"flag": ":flag_mx:", "demonym": "Mexican"},
    "United-States":          {"flag": ":flag_us:", "demonym": "American"},
    "Curaçao":                {"flag": ":flag_cw:", "demonym": "Curaçaoan"},
    "Haiti":                  {"flag": ":flag_ht:", "demonym": "Haitian"},
    "Panama":                 {"flag": ":flag_pa:", "demonym": "Panamanian"},
    # AFC (9)
    "Australia":              {"flag": ":flag_au:", "demonym": "Australian"},
    "Iraq":                   {"flag": ":flag_iq:", "demonym": "Iraqi"},
    "Iran":                   {"flag": ":flag_ir:", "demonym": "Iranian"},
    "Japan":                  {"flag": ":flag_jp:", "demonym": "Japanese"},
    "Jordan":                 {"flag": ":flag_jo:", "demonym": "Jordanian"},
    "South-Korea":            {"flag": ":flag_kr:", "demonym": "South Korean"},
    "Qatar":                  {"flag": ":flag_qa:", "demonym": "Qatari"},
    "Saudi-Arabia":           {"flag": ":flag_sa:", "demonym": "Saudi Arabian"},
    "Uzbekistan":             {"flag": ":flag_uz:", "demonym": "Uzbek"},
    # CAF (10)
    "Algeria":                {"flag": ":flag_dz:", "demonym": "Algerian"},
    "Cape-Verde":             {"flag": ":flag_cv:", "demonym": "Cape Verdean"},
    "DR-Congo":               {"flag": ":flag_cd:", "demonym": "Congolese"},
    "Ivory-Coast":            {"flag": ":flag_ci:", "demonym": "Ivorian"},
    "Egypt":                  {"flag": ":flag_eg:", "demonym": "Egyptian"},
    "Ghana":                  {"flag": ":flag_gh:", "demonym": "Ghanaian"},
    "Morocco":                {"flag": ":flag_ma:", "demonym": "Moroccan"},
    "Senegal":                {"flag": ":flag_sn:", "demonym": "Senegalese"},
    "South-Africa":           {"flag": ":flag_za:", "demonym": "South African"},
    "Tunisia":                {"flag": ":flag_tn:", "demonym": "Tunisian"},
    # CONMEBOL (6)
    "Argentina":              {"flag": ":flag_ar:", "demonym": "Argentine"},
    "Brazil":                 {"flag": ":flag_br:", "demonym": "Brazilian"},
    "Colombia":               {"flag": ":flag_co:", "demonym": "Colombian"},
    "Ecuador":                {"flag": ":flag_ec:", "demonym": "Ecuadorian"},
    "Paraguay":               {"flag": ":flag_py:", "demonym": "Paraguayan"},
    "Uruguay":                {"flag": ":flag_uy:", "demonym": "Uruguayan"},
    # OFC (1)
    "New-Zealand":            {"flag": ":flag_nz:", "demonym": "New Zealander"},
    # UEFA (16)
    "Austria":                {"flag": ":flag_at:", "demonym": "Austrian"},
    "Belgium":                {"flag": ":flag_be:", "demonym": "Belgian"},
    "Bosnia-and-Herzegovina": {"flag": ":flag_ba:", "demonym": "Bosnian"},
    "Croatia":                {"flag": ":flag_hr:", "demonym": "Croatian"},
    "Czech-Republic":         {"flag": ":flag_cz:", "demonym": "Czech"},
    "England":                {"flag": ":england:", "demonym": "English"},
    "France":                 {"flag": ":flag_fr:", "demonym": "French"},
    "Germany":                {"flag": ":flag_de:", "demonym": "German"},
    "Netherlands":            {"flag": ":flag_nl:", "demonym": "Dutch"},
    "Norway":                 {"flag": ":flag_no:", "demonym": "Norwegian"},
    "Portugal":               {"flag": ":flag_pt:", "demonym": "Portuguese"},
    "Scotland":               {"flag": ":scotland:", "demonym": "Scottish"},
    "Spain":                  {"flag": ":flag_es:", "demonym": "Spanish"},
    "Sweden":                 {"flag": ":flag_se:", "demonym": "Swedish"},
    "Switzerland":            {"flag": ":flag_ch:", "demonym": "Swiss"},
    "Turkey":                 {"flag": ":flag_tr:", "demonym": "Turkish"},
}

NUM_TEAMS = len(COUNTRIES)
NICKNAME_MAX = 32  # Discord nickname character cap

# Sorted longest-first incase there's ever an overlap (I cannot think of any though)
_DEMONYM_PREFIXES = sorted(
    {info["demonym"] for info in COUNTRIES.values()},
    key=len, reverse=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_flag(country_name):
    return COUNTRIES[country_name]["flag"]


def flag_mention(role):
    """'flag @Role' (standard way to reference a team in user-facing messages.)"""
    return f"{get_flag(role.name)} {role.mention}"


def get_demonym(country_name):
    return COUNTRIES[country_name]["demonym"]


def strip_known_demonym(nickname):
    for demonym in _DEMONYM_PREFIXES:
        prefix = f"{demonym} "
        if nickname.startswith(prefix):
            return nickname[len(prefix):]
    return nickname


def demonym_nickname(country_name, current_nick, strip=True):
    """Adds a Denonym prefix to the nickname, e.g. "Scottish Bort" or "Bort" -> "English Bort"."""
    base = current_nick
    if strip:
        base = strip_known_demonym(base)
    return f"{get_demonym(country_name)} {base}"[:NICKNAME_MAX]


def get_round_by_alias(alias):
    key = alias.lower().replace(" ", "").replace("_", "").replace("-", "")
    name = ROUND_ALIASES.get(key)
    if name is None:
        return None
    for i, rnd in enumerate(ROUNDS):
        if rnd.name == name:
            return i, rnd
    return None


def resolve_role_token(guild, token):
    """Resolve a single token to a discord.Role. Accepts:
       - role mentions like '<@&123456>'
       - plain role names (exact match, case sensitive)
    Returns None if not found."""
    token = token.strip()
    if token.startswith("<@&") and token.endswith(">"):
        try:
            return guild.get_role(int(token[3:-1]))
        except ValueError:
            return None
    return discord.utils.get(guild.roles, name=token)


def resolve_user_token(guild, token):
    """Resolve a single token to a discord.Member. Accepts:
       - user mentions like '<@123456>' or '<@!123456>'
       - raw user IDs
       - exact display_name / username match
    Returns None if not found."""
    token = token.strip()
    if token.startswith("<@") and token.endswith(">"):
        inner = token[2:-1]
        if inner.startswith("!"):
            inner = inner[1:]
        try:
            return guild.get_member(int(inner))
        except ValueError:
            return None
    try:
        return guild.get_member(int(token))
    except ValueError:
        pass
    return (discord.utils.get(guild.members, display_name=token)
            or discord.utils.get(guild.members, name=token))


def get_loss_round_index(role_colour):
    for i, rnd in enumerate(ROUNDS):
        if role_colour == discord.Colour(rnd.loss_colour):
            return i
    return None


def potential_prize_for_user(user):
    """If the user's currently-active team turns out to be the eventual winner,
    return the £ they would receive. Determined by their LATEST loss-colour
    role (the most recent round in which one of their teams was eliminated).
    Users with no loss-colour roles have been on their active team since the
    start, so they get START_PRIZE."""
    latest_idx = -1
    for role in user.roles:
        idx = get_loss_round_index(role.colour)
        if idx is not None and idx > latest_idx:
            latest_idx = idx
    if latest_idx == -1:
        return START_PRIZE
    return ROUNDS[latest_idx].join_winner_prize


# ---------------------------------------------------------------------------
# Cog
# ---------------------------------------------------------------------------

class Sweepstake(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("sweepstake.py loaded")

    def get_flag(self, country):
        return get_flag(country)

    @commands.command()
    @commands.check(is_admin)
    async def checkroles(self, ctx):
        for country in COUNTRIES:
            role = discord.utils.get(ctx.guild.roles, name=country)
            if role is None:
                await ctx.reply(f"Could not find role: {country}")
                return
        current_msg = "All country roles found\n"

        paid_role = discord.utils.get(ctx.guild.roles, name="Paid")
        if paid_role is None:
            await ctx.reply(current_msg + "No 'Paid' rank to check nicknames against.")
            return

        max_demonym_len = max(len(d) for d in _DEMONYM_PREFIXES)
        nick_budget = NICKNAME_MAX - max_demonym_len - 1  # -1 for the joining space

        too_long = [u for u in paid_role.members if len(u.display_name) > nick_budget]
        if too_long:
            report = "\n> ".join(
                f"{u.mention} ({len(u.display_name)} chars)" for u in too_long
            )
            await ctx.reply(
                current_msg +
                f"These paid nicknames would overflow with the longest demonym \n"
                f"(budget is {nick_budget} chars; longest demonym is {max_demonym_len}):\n> {report}"
            )
            return

        await ctx.reply(current_msg + "Every paid nickname fits any demonym.")

    @commands.command()
    @commands.check(is_admin)
    async def startsweepstake(self, ctx):
        role_list = [role for role in ctx.guild.roles if role.name in COUNTRIES]
        if len(role_list) != NUM_TEAMS:
            await ctx.reply(f"{len(role_list)} country ranks found. Expected {NUM_TEAMS}")
            return

        paid_role = discord.utils.get(ctx.guild.roles, name="Paid")
        if paid_role is None:
            await ctx.reply("No 'Paid' rank found")
            return
        paid_users = list(paid_role.members)
        if len(paid_users) != NUM_TEAMS:
            await ctx.reply(f"{len(paid_users)} users found with 'Paid' rank. Expected {NUM_TEAMS}")
            return

        random.shuffle(paid_users)
        random.shuffle(role_list)

        for user, role in zip(paid_users, role_list):
            await user.add_roles(role)
            new_nick = demonym_nickname(role.name, user.display_name, strip=False)
            if new_nick is not None:
                try:
                    await user.edit(nick=new_nick)
                except:
                    pass  # bot can't rename users above it in the role hierarchy
            await ctx.channel.send(f"{user.mention} has been given: {flag_mention(role)}")
            await asyncio.sleep(1.5 * 60)

        lines = [f"{flag_mention(role)}: {user.mention}" for user, role in zip(paid_users, role_list)]
        await ctx.channel.send("**Initial Teams**\n" + "\n".join(lines))

    @commands.command()
    @commands.check(is_admin)
    async def addrole(self, ctx, role_token: str):
        role = resolve_role_token(ctx.guild, role_token)
        if role is None:
            await ctx.reply(f"Could not find role: {role_token}")
            return
        await ctx.author.add_roles(role)

    @commands.command()
    @commands.check(is_admin)
    async def adddemonym(self, ctx, user_token: str, role_token: str):
        """Test: prefix the role's demonym onto the user's nickname.
        Usage: ?adddemonym @user @CountryRole"""
        member = resolve_user_token(ctx.guild, user_token)
        if member is None:
            await ctx.reply(f"Could not find user: {user_token}")
            return
        role = resolve_role_token(ctx.guild, role_token)
        if role is None:
            await ctx.reply(f"Could not find role: {role_token}")
            return
        if role.name not in COUNTRIES:
            await ctx.reply(f"{role.name} is not a country role in COUNTRIES.")
            return
        new_nick = demonym_nickname(role.name, member.display_name)
        try:
            await member.edit(nick=new_nick)
            await ctx.reply(f"{member.mention} -> `{new_nick}`")
        except Exception as e:
            await ctx.reply(f"Failed to rename {member.mention}: {type(e).__name__}: {e}")

    @commands.command()
    @commands.check(is_admin)
    async def stripdemonym(self, ctx, user_token: str):
        """Test: strip any known demonym prefix from the user's nickname.
        Usage: ?stripdemonym @user"""
        member = resolve_user_token(ctx.guild, user_token)
        if member is None:
            await ctx.reply(f"Could not find user: {user_token}")
            return
        stripped = strip_known_demonym(member.display_name)
        if stripped == member.display_name:
            await ctx.reply(f"No known demonym prefix on {member.mention}'s nickname.")
            return
        try:
            await member.edit(nick=stripped)
            await ctx.reply(f"{member.mention} -> `{stripped}`")
        except Exception as e:
            await ctx.reply(f"Failed to rename {member.mention}: {type(e).__name__}: {e}")

    @commands.command()
    @commands.check(is_admin)
    async def postcurrentroles(self, ctx):
        active_colour = discord.Colour(ACTIVE_COLOUR)
        role_list = [role for role in ctx.guild.roles
                     if role.name in COUNTRIES and role.colour == active_colour]

        role_str_list = []
        for role in role_list:
            member_mentions = [member.mention for member in role.members]
            role_str = f"{flag_mention(role)}:\n> " + "\n> ".join(member_mentions)
            role_str_list.append(role_str)

        msg = "Current Teams:\n" + "\n".join(role_str_list)
        await ctx.send(msg)

    @commands.command()
    @commands.check(is_admin)
    async def addresult(self, ctx, team1: str, team2: str,
                        round_name: str = "r32", channel_id: str = None):
        """team1 beats team2. team2 is eliminated; if it's a knockout round,
        team2's users gain team1's role. Group stage uses a separate command.

        team1, team2: @mention or plain role name (strings).
        round_name: r32 | r16 | qf | sf | f  (default r32)
        """
        match = get_round_by_alias(round_name)
        if match is None:
            await ctx.reply(f"Unknown round: {round_name!r}. Use one of: r32, r16, qf, sf, f")
            return
        _, rnd = match
        if rnd.name == "Group Stage":
            await ctx.reply("Use !postgroupstagereassignment for the group stage.")
            return

        role1 = resolve_role_token(ctx.guild, team1)
        role2 = resolve_role_token(ctx.guild, team2)
        if role1 is None or role2 is None:
            await ctx.reply(f"Could not find one of: {team1}, {team2}")
            return

        reassigned_users = []
        if rnd.reassign_after:
            for user in role2.members:
                reassigned_users.append(user.mention)
                await user.add_roles(role1)

        await role2.edit(colour=discord.Colour(rnd.loss_colour))
        try:
            await role1.edit(position=NUM_TEAMS)
        except Exception as e:
            await ctx.reply(f"Position edit failed ({type(e).__name__}: {e}): Continuing.")

        if channel_id is not None:
            team_channel = self.client.get_channel(int(channel_id))
            if team_channel is None:
                await ctx.reply(f"Channel {channel_id} not found — skipping announcement.")
            else:
                if rnd.name == "Final":
                    msg0 = f"{flag_mention(role1)} has won the {TOURNAMENT_NAME}"
                elif rnd.reassign_after and reassigned_users:
                    msg0 = (f"{flag_mention(role2)} has been eliminated.\n"
                            f"The following people have been reassigned to {flag_mention(role1)}: \n> "
                            + "\n> ".join(reassigned_users))
                else:
                    msg0 = f"{flag_mention(role2)} has been eliminated."
                await team_channel.send(msg0)

        return [role1, role2]

    @commands.command()
    @commands.check(is_admin)
    async def markgroupstageout(self, ctx, team_token: str, channel_id: str = None):
        """Mark a single team as eliminated at the group stage.
        team_token: @mention or plain role name (string).
        channel_id: optional; if given, posts an elimination announcement there."""
        role = resolve_role_token(ctx.guild, team_token)
        if role is None:
            await ctx.reply(f"Could not find role: {team_token}")
            return
        await role.edit(colour=discord.Colour(ROUNDS[0].loss_colour))
        if channel_id is not None:
            team_channel = self.client.get_channel(int(channel_id))
            if team_channel is None:
                await ctx.reply(f"Channel {channel_id} not found — skipping announcement.")
                return
            await team_channel.send(f"{flag_mention(role)} has been eliminated at the group stage.")

    @commands.command()
    @commands.check(is_admin)
    async def postgroupstagereassignment(self, ctx, channel_id: str, *, matchups_text: str):
        """Randomly pair each group-stage-eliminated team with an R32 matchup
        and post the announcement to the given channel. Mark the 16 eliminated
        teams first via !markgroupstageout. Then call with channel_id followed
        by the 16 R32 matchups, one per line (each team can be an @mention or
        a plain role name):

            !postgroupstagereassignment 1234567890
            @Portugal vs @Slovenia
            @Spain vs @Germany
            ..."""
        group_out_colour = discord.Colour(ROUNDS[0].loss_colour)
        eliminated_roles = [role for role in ctx.guild.roles
                            if role.name in COUNTRIES and role.colour == group_out_colour]
        if len(eliminated_roles) != 16:
            await ctx.reply(f"Expected 16 teams with the Group Stage colour, "
                            f"found {len(eliminated_roles)}. Use !markgroupstageout first.")
            return

        matchups = []
        for line in matchups_text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            lower = line.lower()
            sep = lower.find(" vs ")
            if sep == -1:
                await ctx.reply(f"Invalid matchup line: {line!r}. Expected '<Team A> vs <Team B>'.")
                return
            token_a = line[:sep].strip()
            token_b = line[sep + 4:].strip()
            role_a = resolve_role_token(ctx.guild, token_a)
            role_b = resolve_role_token(ctx.guild, token_b)
            if role_a is None:
                await ctx.reply(f"Could not find: {token_a}")
                return
            if role_b is None:
                await ctx.reply(f"Could not find: {token_b}")
                return
            matchups.append((role_a, role_b))

        if len(matchups) != 16:
            await ctx.reply(f"Expected 16 matchups, found {len(matchups)}.")
            return

        seen = set()
        for a, b in matchups:
            for r in (a, b):
                if r.id in seen:
                    await ctx.reply(f"Duplicate team in matchups: {r.name}")
                    return
                seen.add(r.id)
        for r in eliminated_roles:
            if r.id in seen:
                await ctx.reply(f"Eliminated team {r.name} also appears in matchups.")
                return

        random.shuffle(eliminated_roles)
        random.shuffle(matchups)

        lines = []
        for eliminated, (a, b) in zip(eliminated_roles, matchups):
            for member in eliminated.members:
                await member.add_roles(a, b)
            lines.append(
                f"{flag_mention(eliminated)} will be reassigned to the winner of:\n"
                f"{flag_mention(a)} vs {flag_mention(b)}"
            )
        team_channel = self.client.get_channel(int(channel_id))
        if team_channel is None:
            await ctx.reply(f"Channel {channel_id} not found — reassignments applied but no announcement posted.")
            return
        await team_channel.send("**Group Stage Reassignments**\n\n" + "\n\n".join(lines))

    @commands.command()
    @commands.check(is_admin)
    async def postpotwins(self, ctx):
        active_colour = discord.Colour(ACTIVE_COLOUR)
        paid_role = discord.utils.get(ctx.guild.roles, name="Paid")
        paid_users = paid_role.members

        # user -> (active country roles they hold, potential prize if any of them wins)
        user_info = {}
        for user in paid_users:
            active_teams = [role for role in user.roles
                            if role.name in COUNTRIES and role.colour == active_colour]
            user_info[user.mention] = (active_teams, potential_prize_for_user(user))

        team_dict = {}
        for user_mention, (active_teams, prize) in user_info.items():
            for team in active_teams:
                team_dict.setdefault(team, []).append((prize, user_mention))

        prize_str_list = []
        for team, entries in team_dict.items():
            entries.sort(reverse=True)
            user_prize_str_list = [f"{user_mention}: £{prize}" for prize, user_mention in entries]
            prize_str_list.append(f"{flag_mention(team)}:\n> " + "\n> ".join(user_prize_str_list))

        header = "Potential Prizes" if len(prize_str_list) != 1 else "Prizes"
        msg = f"{header}:\n" + "\n".join(prize_str_list)
        await ctx.send(msg)

    @commands.command()
    @commands.check(is_admin)
    async def resetroles(self, ctx):
        """Strip every paid user of their country roles and remove any demonym
        prefix from their nickname. For resetting between tournaments / tests."""
        paid_role = discord.utils.get(ctx.guild.roles, name="Paid")
        if paid_role is None:
            await ctx.reply("No 'Paid' rank found.")
            return

        country_role_ids = {role.id for role in ctx.guild.roles if role.name in COUNTRIES}

        for member in list(paid_role.members):
            to_remove = [role for role in member.roles if role.id in country_role_ids]
            if to_remove:
                await member.remove_roles(*to_remove)

            stripped = strip_known_demonym(member.display_name)
            if stripped != member.display_name:
                try:
                    await member.edit(nick=stripped)
                except :
                    pass

        await ctx.reply("Cleared country roles and stripped demonym prefixes from paid users.")

    @commands.command()
    @commands.check(is_admin)
    async def resetcolors(self, ctx):
        role_list = [role for role in ctx.guild.roles if role.name in COUNTRIES]
        if len(role_list) != NUM_TEAMS:
            await ctx.reply(f"{len(role_list)} country ranks found. Expected {NUM_TEAMS}")
            return
        for role in role_list:
            await role.edit(colour=discord.Colour(ACTIVE_COLOUR))

    @commands.command()
    @commands.check(is_admin)
    async def createroles(self, ctx):
        role_list = [role for role in ctx.guild.roles if role.name in COUNTRIES]
        if len(role_list) != 0:
            await ctx.reply(f"some country ranks were already found: {[role.name for role in role_list]}.")
            return
        for country in COUNTRIES:
            await ctx.guild.create_role(name=country, colour=discord.Colour(ACTIVE_COLOUR))

    @commands.command()
    @commands.check(is_admin)
    async def deleteroles(self, ctx):
        role_list = [role for role in ctx.guild.roles if role.name in COUNTRIES]
        for role in role_list:
            await role.delete()


async def setup(client):
    await client.add_cog(Sweepstake(client))
