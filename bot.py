import discord
from discord.ext import commands
from discord import app_commands
import json, os, random, string, datetime
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return 'D4vid Hub Bot is alive!'

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

BOT_TOKEN   = os.environ["BOT_TOKEN"]
OWNER_ID    = 1273331857584422955
GUILD_ID    = 1502262210871693312
SCRIPT_LINK = "https://pastebin.com/raw/Gpds4EMc"
SCRIPT_LOADSTRING = 'loadstring(game:HttpGet("' + SCRIPT_LINK + '"))()'
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"keys": {}, "whitelist": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def is_owner():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(embed=error_embed("❌ Non hai i permessi."), ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

COLOR_RED=0xC81E1E; COLOR_GREEN=0x16A34A; COLOR_YELLOW=0xCA8A04; COLOR_DARK=0x111111

def base_embed(title, desc="", color=COLOR_DARK):
    e = discord.Embed(title=title, description=desc, color=color)
    e.set_footer(text="D4vid Hub • Control Panel")
    e.timestamp = datetime.datetime.utcnow()
    return e

def success_embed(msg): return base_embed("✅  Successo", msg, COLOR_GREEN)
def error_embed(msg): return base_embed("❌  Errore", msg, COLOR_RED)
def info_embed(title, msg): return base_embed(title, msg, COLOR_DARK)

def gen_key(prefix="D4VID"):
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return f"{prefix}-{rand[:4]}-{rand[4:8]}-{rand[8:]}"

@tree.command(name="genkey", description="[OWNER] Genera una nuova chiave")
@is_owner()
async def genkey(interaction: discord.Interaction, utente: discord.User = None):
    data = load_data()
    key = gen_key()
    data["keys"][key] = {"used": False, "assigned_to": str(utente.id) if utente else None, "created_at": str(datetime.datetime.utcnow()), "redeemed_by": None}
    save_data(data)
    e = base_embed("🔑  Chiave Generata", f"```{key}```", COLOR_YELLOW)
    if utente: e.add_field(name="Assegnata a", value=utente.mention)
    await interaction.response.send_message(embed=e, ephemeral=True)
    if utente:
        try:
            dm = base_embed("🔑  Hai ricevuto una chiave D4vid Hub", color=COLOR_YELLOW)
            dm.add_field(name="Chiave", value=f"```{key}```", inline=False)
            dm.add_field(name="Come usarla", value="Usa `/redeem <chiave>` nel server", inline=False)
            await utente.send(embed=dm)
        except: pass

@tree.command(name="redeem", description="Riscatta una chiave per accedere alla script")
async def redeem(interaction: discord.Interaction, chiave: str):
    data = load_data()
    chiave = chiave.strip().upper()
    if chiave not in data["keys"]:
        await interaction.response.send_message(embed=error_embed("Chiave non valida."), ephemeral=True); return
    if data["keys"][chiave]["used"]:
        await interaction.response.send_message(embed=error_embed("Chiave già usata."), ephemeral=True); return
    user_id = str(interaction.user.id)
    if user_id in data["whitelist"]:
        await interaction.response.send_message(embed=error_embed("Sei già nella whitelist!"), ephemeral=True); return
    data["keys"][chiave]["used"] = True
    data["keys"][chiave]["redeemed_by"] = user_id
    data["whitelist"].append(user_id)
    save_data(data)
    await interaction.response.send_message(embed=success_embed("Sei nella whitelist! Usa `/getscript`"), ephemeral=True)

@tree.command(name="getscript", description="Ottieni la script (solo whitelist)")
async def getscript(interaction: discord.Interaction):
    data = load_data()
    if str(interaction.user.id) not in data["whitelist"] and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(embed=error_embed("Non sei nella whitelist."), ephemeral=True); return
    e = base_embed("📜  D4vid Hub Script", color=COLOR_RED)
    e.add_field(name="Loadstring", value=f"```lua\n{SCRIPT_LOADSTRING}\n```", inline=False)
    await interaction.response.send_message(embed=e, ephemeral=True)

@tree.command(name="whitelist_add", description="[OWNER] Aggiungi utente alla whitelist")
@is_owner()
async def whitelist_add(interaction: discord.Interaction, utente: discord.User):
    data = load_data()
    if str(utente.id) in data["whitelist"]:
        await interaction.response.send_message(embed=error_embed(f"{utente.mention} già nella whitelist."), ephemeral=True); return
    data["whitelist"].append(str(utente.id)); save_data(data)
    await interaction.response.send_message(embed=success_embed(f"{utente.mention} aggiunto."), ephemeral=True)

@tree.command(name="whitelist_remove", description="[OWNER] Rimuovi utente dalla whitelist")
@is_owner()
async def whitelist_remove(interaction: discord.Interaction, utente: discord.User):
    data = load_data()
    if str(utente.id) not in data["whitelist"]:
        await interaction.response.send_message(embed=error_embed(f"{utente.mention} non nella whitelist."), ephemeral=True); return
    data["whitelist"].remove(str(utente.id)); save_data(data)
    await interaction.response.send_message(embed=success_embed(f"{utente.mention} rimosso."), ephemeral=True)

@tree.command(name="whitelist_check", description="Controlla se sei nella whitelist")
async def whitelist_check(interaction: discord.Interaction, utente: discord.User = None):
    data = load_data(); target = utente or interaction.user
    is_wl = str(target.id) in data["whitelist"] or target.id == OWNER_ID
    stato = "✅ Nella whitelist" if is_wl else "❌ Non nella whitelist"
    await interaction.response.send_message(embed=base_embed("🔍 Check", f"{target.mention}\n{stato}", COLOR_GREEN if is_wl else COLOR_RED), ephemeral=True)

@tree.command(name="whitelist_list", description="[OWNER] Lista whitelist")
@is_owner()
async def whitelist_list(interaction: discord.Interaction):
    data = load_data(); wl = data["whitelist"]
    txt = "\n".join([f"`{uid}`" for uid in wl[:30]]) if wl else "Vuota"
    await interaction.response.send_message(embed=info_embed("📋 Whitelist", f"**{len(wl)} utenti**\n{txt}"), ephemeral=True)

@tree.command(name="keys_list", description="[OWNER] Lista chiavi")
@is_owner()
async def keys_list(interaction: discord.Interaction):
    data = load_data(); keys = data["keys"]
    if not keys:
        await interaction.response.send_message(embed=info_embed("🔑 Chiavi", "Nessuna chiave."), ephemeral=True); return
    lines = [f"`{k}` — {'🟢 Usata' if v['used'] else '🟡 Libera'}" for k,v in list(keys.items())[:15]]
    await interaction.response.send_message(embed=info_embed("🔑 Chiavi", "\n".join(lines)), ephemeral=True)

@tree.command(name="revoke_key", description="[OWNER] Elimina una chiave")
@is_owner()
async def revoke_key(interaction: discord.Interaction, chiave: str):
    data = load_data(); chiave = chiave.strip().upper()
    if chiave not in data["keys"]:
        await interaction.response.send_message(embed=error_embed("Chiave non trovata."), ephemeral=True); return
    del data["keys"][chiave]; save_data(data)
    await interaction.response.send_message(embed=success_embed(f"Chiave `{chiave}` eliminata."), ephemeral=True)

class PanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=120)

    @discord.ui.button(label="🔑 Genera Chiave", style=discord.ButtonStyle.danger)
    async def gen_key_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(embed=error_embed("Solo l'owner."), ephemeral=True); return
        data = load_data(); key = gen_key()
        data["keys"][key] = {"used": False, "assigned_to": None, "created_at": str(datetime.datetime.utcnow()), "redeemed_by": None}
        save_data(data)
        await interaction.response.send_message(embed=base_embed("🔑 Nuova Chiave", f"```{key}```", COLOR_YELLOW), ephemeral=True)

    @discord.ui.button(label="📋 Whitelist", style=discord.ButtonStyle.secondary)
    async def wl_list_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(embed=error_embed("Solo l'owner."), ephemeral=True); return
        data = load_data(); wl = data["whitelist"]
        txt = "\n".join([f"`{uid}`" for uid in wl[:20]]) if wl else "Vuota"
        await interaction.response.send_message(embed=info_embed("📋 Whitelist", f"**{len(wl)} utenti**\n{txt}"), ephemeral=True)

    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.secondary)
    async def stats_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data(); keys = data["keys"]
        used = sum(1 for v in keys.values() if v["used"])
        e = base_embed("📊 Stats", color=COLOR_DARK)
        e.add_field(name="👥 Whitelist", value=str(len(data["whitelist"])), inline=True)
        e.add_field(name="🔑 Chiavi", value=str(len(keys)), inline=True)
        e.add_field(name="🟢 Usate", value=str(used), inline=True)
        e.add_field(name="🟡 Libere", value=str(len(keys)-used), inline=True)
        await interaction.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(label="📜 Ottieni Script", style=discord.ButtonStyle.success)
    async def get_script_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        if str(interaction.user.id) not in data["whitelist"] and interaction.user.id != OWNER_ID:
            await interaction.response.send_message(embed=error_embed("Non sei nella whitelist."), ephemeral=True); return
        e = base_embed("📜 Script", color=COLOR_RED)
        e.add_field(name="Loadstring", value=f"```lua\n{SCRIPT_LOADSTRING}\n```", inline=False)
        await interaction.response.send_message(embed=e, ephemeral=True)

@tree.command(name="panel", description="Apre il control panel di D4vid Hub")
async def panel(interaction: discord.Interaction):
    e = base_embed("🎮  D4vid Hub — Control Panel", "Usa i pulsanti per gestire whitelist e script.", COLOR_RED)
    e.add_field(name="👑 Owner", value=f"<@{OWNER_ID}>", inline=True)
    e.add_field(name="📜 Script", value="D4vid Hub", inline=True)
    await interaction.response.send_message(embed=e, view=PanelView(), ephemeral=True)

@bot.event
async def on_ready():
    print(f"[D4vid Hub Bot] Online come {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        tree.copy_global_to(guild=guild)
        synced = await tree.sync(guild=guild)
        print(f"Sincronizzati {len(synced)} comandi")
    except Exception as e:
        print(f"Errore sync: {e}")
    await bot.change_presence(activity=discord.Game(name="D4vid Hub 🎮"))

keep_alive()
bot.run(BOT_TOKEN)
