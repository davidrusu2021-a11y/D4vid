import discord
from discord.ext import commands
from discord import app_commands
import json, os, random, string, datetime

from flask import Flask
from threading import Thread

app = Flask(’’)

@app.route(’/’)
def home():
return ‘D4vid Hub Bot is alive!’

def run():
app.run(host=‘0.0.0.0’, port=8080)

def keep_alive():
t = Thread(target=run)
t.start()

# ──────────────────────────────────────────

# CONFIG  –  modifica questi valori

# ──────────────────────────────────────────

BOT_TOKEN   = “INSERISCI_NUOVO_TOKEN_QUI”   # ⚠️ Resetta il token sul Developer Portal prima!
OWNER_ID    = 1273331857584422955
GUILD_ID    = 1502262210871693312

# Link / testo della script da distribuire

SCRIPT_LINK = “https://pastebin.com/raw/Gpds4EMc”
SCRIPT_LOADSTRING = ‘loadstring(game:HttpGet(”’ + SCRIPT_LINK + ‘”))()’

DATA_FILE = “data.json”

# ──────────────────────────────────────────

# PERSISTENZA  (file JSON)

# ──────────────────────────────────────────

def load_data():
if not os.path.exists(DATA_FILE):
return {“keys”: {}, “whitelist”: []}
with open(DATA_FILE, “r”) as f:
return json.load(f)

def save_data(data):
with open(DATA_FILE, “w”) as f:
json.dump(data, f, indent=2)

# ──────────────────────────────────────────

# BOT SETUP

# ──────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=”!”, intents=intents)
tree = bot.tree

def is_owner():
async def predicate(interaction: discord.Interaction):
if interaction.user.id != OWNER_ID:
await interaction.response.send_message(
embed=error_embed(“❌ Non hai i permessi per usare questo comando.”),
ephemeral=True
)
return False
return True
return app_commands.check(predicate)

# ──────────────────────────────────────────

# EMBED HELPERS

# ──────────────────────────────────────────

COLOR_RED    = 0xC81E1E
COLOR_GREEN  = 0x16A34A
COLOR_YELLOW = 0xCA8A04
COLOR_DARK   = 0x111111

def base_embed(title, desc=””, color=COLOR_DARK):
e = discord.Embed(title=title, description=desc, color=color)
e.set_footer(text=“D4vid Hub • Control Panel”)
e.timestamp = datetime.datetime.utcnow()
return e

def success_embed(msg):
return base_embed(“✅  Successo”, msg, COLOR_GREEN)

def error_embed(msg):
return base_embed(“❌  Errore”, msg, COLOR_RED)

def info_embed(title, msg):
return base_embed(title, msg, COLOR_DARK)

# ──────────────────────────────────────────

# KEY GENERATOR

# ──────────────────────────────────────────

def gen_key(prefix=“D4VID”):
rand = ‘’.join(random.choices(string.ascii_uppercase + string.digits, k=12))
return f”{prefix}-{rand[:4]}-{rand[4:8]}-{rand[8:]}”

# ══════════════════════════════════════════

# COMANDI SLASH  –  WHITELIST

# ══════════════════════════════════════════

@tree.command(name=“genkey”, description=”[OWNER] Genera una nuova chiave di accesso”)
@app_commands.describe(utente=“Utente a cui assegnare la chiave (opzionale)”)
@is_owner()
async def genkey(interaction: discord.Interaction, utente: discord.User = None):
data = load_data()
key = gen_key()
user_id = str(utente.id) if utente else None

```
data["keys"][key] = {
    "used": False,
    "assigned_to": user_id,
    "assigned_name": str(utente) if utente else None,
    "created_at": str(datetime.datetime.utcnow()),
    "redeemed_by": None
}
save_data(data)

e = base_embed("🔑  Chiave Generata", color=COLOR_YELLOW)
e.add_field(name="Chiave", value=f"```{key}```", inline=False)
if utente:
    e.add_field(name="Assegnata a", value=utente.mention, inline=True)
e.add_field(name="Stato", value="🟡 Non ancora usata", inline=True)

await interaction.response.send_message(embed=e, ephemeral=True)

# DM la chiave all'utente se specificato
if utente:
    try:
        dm_e = base_embed("🔑  Hai ricevuto una chiave D4vid Hub", color=COLOR_YELLOW)
        dm_e.add_field(name="La tua chiave", value=f"```{key}```", inline=False)
        dm_e.add_field(name="Come usarla", value="Vai nel server e usa `/redeem <chiave>`", inline=False)
        await utente.send(embed=dm_e)
    except:
        pass
```

@tree.command(name=“redeem”, description=“Riscatta una chiave per ottenere l’accesso alla script”)
@app_commands.describe(chiave=“La tua chiave di accesso”)
async def redeem(interaction: discord.Interaction, chiave: str):
data = load_data()
chiave = chiave.strip().upper()

```
if chiave not in data["keys"]:
    await interaction.response.send_message(embed=error_embed("Chiave non valida."), ephemeral=True)
    return

key_data = data["keys"][chiave]

if key_data["used"]:
    await interaction.response.send_message(embed=error_embed("Questa chiave è già stata usata."), ephemeral=True)
    return

user_id = str(interaction.user.id)

# Controlla se già in whitelist
if user_id in data["whitelist"]:
    await interaction.response.send_message(embed=error_embed("Sei già nella whitelist!"), ephemeral=True)
    return

# Riscatta
key_data["used"] = True
key_data["redeemed_by"] = user_id
key_data["redeemed_at"] = str(datetime.datetime.utcnow())
data["whitelist"].append(user_id)
save_data(data)

e = success_embed(f"Sei ora nella **whitelist** di D4vid Hub!\nUsa `/getscript` per ottenere la script.")
await interaction.response.send_message(embed=e, ephemeral=True)
```

@tree.command(name=“getscript”, description=“Ottieni il loadstring della script (solo whitelist)”)
async def getscript(interaction: discord.Interaction):
data = load_data()
user_id = str(interaction.user.id)

```
if user_id not in data["whitelist"] and interaction.user.id != OWNER_ID:
    await interaction.response.send_message(
        embed=error_embed("Non sei nella whitelist.\nUsa `/redeem <chiave>` per ottenere l'accesso."),
        ephemeral=True
    )
    return

e = base_embed("📜  D4vid Hub — Script", color=COLOR_RED)
e.add_field(name="Loadstring", value=f"```lua\n{SCRIPT_LOADSTRING}\n```", inline=False)
e.add_field(name="⚠️ Avviso", value="Non condividere questo messaggio con nessuno.", inline=False)
await interaction.response.send_message(embed=e, ephemeral=True)
```

# ══════════════════════════════════════════

# COMANDI SLASH  –  GESTIONE WHITELIST

# ══════════════════════════════════════════

@tree.command(name=“whitelist_add”, description=”[OWNER] Aggiunge un utente alla whitelist manualmente”)
@app_commands.describe(utente=“Utente da aggiungere”)
@is_owner()
async def whitelist_add(interaction: discord.Interaction, utente: discord.User):
data = load_data()
user_id = str(utente.id)

```
if user_id in data["whitelist"]:
    await interaction.response.send_message(embed=error_embed(f"{utente.mention} è già nella whitelist."), ephemeral=True)
    return

data["whitelist"].append(user_id)
save_data(data)
await interaction.response.send_message(embed=success_embed(f"{utente.mention} aggiunto alla whitelist."), ephemeral=True)
```

@tree.command(name=“whitelist_remove”, description=”[OWNER] Rimuove un utente dalla whitelist”)
@app_commands.describe(utente=“Utente da rimuovere”)
@is_owner()
async def whitelist_remove(interaction: discord.Interaction, utente: discord.User):
data = load_data()
user_id = str(utente.id)

```
if user_id not in data["whitelist"]:
    await interaction.response.send_message(embed=error_embed(f"{utente.mention} non è nella whitelist."), ephemeral=True)
    return

data["whitelist"].remove(user_id)
save_data(data)
await interaction.response.send_message(embed=success_embed(f"{utente.mention} rimosso dalla whitelist."), ephemeral=True)
```

@tree.command(name=“whitelist_check”, description=“Controlla se un utente è nella whitelist”)
@app_commands.describe(utente=“Utente da controllare (lascia vuoto per controllarti)”)
async def whitelist_check(interaction: discord.Interaction, utente: discord.User = None):
data = load_data()
target = utente or interaction.user
user_id = str(target.id)
is_wl = user_id in data[“whitelist”] or target.id == OWNER_ID

```
color = COLOR_GREEN if is_wl else COLOR_RED
stato = "✅ Nella whitelist" if is_wl else "❌ Non nella whitelist"
e = base_embed("🔍  Whitelist Check", f"{target.mention}\n{stato}", color)
await interaction.response.send_message(embed=e, ephemeral=True)
```

@tree.command(name=“whitelist_list”, description=”[OWNER] Mostra tutti gli utenti nella whitelist”)
@is_owner()
async def whitelist_list(interaction: discord.Interaction):
data = load_data()
wl = data[“whitelist”]

```
if not wl:
    await interaction.response.send_message(embed=info_embed("📋  Whitelist", "Nessun utente nella whitelist."), ephemeral=True)
    return

lines = [f"`{uid}`" for uid in wl]
chunk = "\n".join(lines[:30])
e = info_embed("📋  Whitelist", f"**{len(wl)} utenti:**\n{chunk}")
if len(wl) > 30:
    e.set_footer(text=f"Mostrati 30/{len(wl)} • D4vid Hub")
await interaction.response.send_message(embed=e, ephemeral=True)
```

@tree.command(name=“keys_list”, description=”[OWNER] Mostra tutte le chiavi generate”)
@is_owner()
async def keys_list(interaction: discord.Interaction):
data = load_data()
keys = data[“keys”]

```
if not keys:
    await interaction.response.send_message(embed=info_embed("🔑  Chiavi", "Nessuna chiave generata."), ephemeral=True)
    return

lines = []
for k, v in list(keys.items())[:15]:
    stato = "🟢 Usata" if v["used"] else "🟡 Libera"
    lines.append(f"`{k}` — {stato}")

e = info_embed("🔑  Chiavi Generate", "\n".join(lines))
e.set_footer(text=f"Totale: {len(keys)} chiavi • D4vid Hub")
await interaction.response.send_message(embed=e, ephemeral=True)
```

@tree.command(name=“revoke_key”, description=”[OWNER] Elimina una chiave”)
@app_commands.describe(chiave=“La chiave da eliminare”)
@is_owner()
async def revoke_key(interaction: discord.Interaction, chiave: str):
data = load_data()
chiave = chiave.strip().upper()

```
if chiave not in data["keys"]:
    await interaction.response.send_message(embed=error_embed("Chiave non trovata."), ephemeral=True)
    return

del data["keys"][chiave]
save_data(data)
await interaction.response.send_message(embed=success_embed(f"Chiave `{chiave}` eliminata."), ephemeral=True)
```

# ══════════════════════════════════════════

# PANNELLO INTERATTIVO  /panel

# ══════════════════════════════════════════

class PanelView(discord.ui.View):
def **init**(self):
super().**init**(timeout=120)

```
@discord.ui.button(label="🔑 Genera Chiave", style=discord.ButtonStyle.danger)
async def gen_key_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(embed=error_embed("Solo l'owner può farlo."), ephemeral=True)
        return
    data = load_data()
    key = gen_key()
    data["keys"][key] = {"used": False, "assigned_to": None, "assigned_name": None,
                          "created_at": str(datetime.datetime.utcnow()), "redeemed_by": None}
    save_data(data)
    e = base_embed("🔑  Nuova Chiave", f"```{key}```", COLOR_YELLOW)
    await interaction.response.send_message(embed=e, ephemeral=True)

@discord.ui.button(label="📋 Lista Whitelist", style=discord.ButtonStyle.secondary)
async def wl_list_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(embed=error_embed("Solo l'owner può farlo."), ephemeral=True)
        return
    data = load_data()
    wl = data["whitelist"]
    txt = "\n".join([f"`{uid}`" for uid in wl[:20]]) if wl else "Vuota"
    e = info_embed("📋  Whitelist", f"**{len(wl)} utenti**\n{txt}")
    await interaction.response.send_message(embed=e, ephemeral=True)

@discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.secondary)
async def stats_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
    data = load_data()
    keys = data["keys"]
    used = sum(1 for v in keys.values() if v["used"])
    free = len(keys) - used
    e = base_embed("📊  Statistiche D4vid Hub", color=COLOR_DARK)
    e.add_field(name="👥 Whitelist", value=str(len(data["whitelist"])), inline=True)
    e.add_field(name="🔑 Chiavi Totali", value=str(len(keys)), inline=True)
    e.add_field(name="🟢 Usate", value=str(used), inline=True)
    e.add_field(name="🟡 Libere", value=str(free), inline=True)
    await interaction.response.send_message(embed=e, ephemeral=True)

@discord.ui.button(label="📜 Ottieni Script", style=discord.ButtonStyle.success)
async def get_script_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
    data = load_data()
    user_id = str(interaction.user.id)
    if user_id not in data["whitelist"] and interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            embed=error_embed("Non sei nella whitelist.\nUsa `/redeem <chiave>`."), ephemeral=True)
        return
    e = base_embed("📜  D4vid Hub Script", color=COLOR_RED)
    e.add_field(name="Loadstring", value=f"```lua\n{SCRIPT_LOADSTRING}\n```", inline=False)
    await interaction.response.send_message(embed=e, ephemeral=True)
```

@tree.command(name=“panel”, description=“Apre il control panel interattivo di D4vid Hub”)
async def panel(interaction: discord.Interaction):
e = base_embed(
“🎮  D4vid Hub — Control Panel”,
“Benvenuto nel pannello di controllo.\nUsa i pulsanti qui sotto per gestire la whitelist e la script.”,
COLOR_RED
)
e.set_thumbnail(url=“https://i.imgur.com/placeholder.png”)
e.add_field(name=“👑 Owner”, value=f”<@{OWNER_ID}>”, inline=True)
e.add_field(name=“📜 Script”, value=“D4vid Hub”, inline=True)
await interaction.response.send_message(embed=e, view=PanelView(), ephemeral=True)

# ══════════════════════════════════════════

# EVENTS

# ══════════════════════════════════════════

@bot.event
async def on_ready():
print(f”[D4vid Hub Bot] Online come {bot.user}”)
try:
if GUILD_ID:
guild = discord.Object(id=GUILD_ID)
tree.copy_global_to(guild=guild)
synced = await tree.sync(guild=guild)
else:
synced = await tree.sync()
print(f”[D4vid Hub Bot] Sincronizzati {len(synced)} comandi slash”)
except Exception as e:
print(f”[D4vid Hub Bot] Errore sync: {e}”)
await bot.change_presence(activity=discord.Game(name=“D4vid Hub 🎮”))

keep_alive()
print(”[D4vid Hub] Avvio bot…”)
try:
bot.run(BOT_TOKEN)
except Exception as e:
print(f”[D4vid Hub] ERRORE AVVIO: {e}”)
import traceback
traceback.print_exc()
