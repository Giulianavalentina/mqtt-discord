import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ui import Button, View
import paho.mqtt.client as mqtt

load_dotenv()  # Carga las variables del archivo .env

print("Bot iniciando...")

# Configuración MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "casa/puerta/luz/control"

# Inicializar cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

# Configuración del bot con intents correctos
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Vista personalizada con botones
class ControlLuzView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Encender", style=discord.ButtonStyle.success, custom_id="encender"))
        self.add_item(Button(label="Apagar", style=discord.ButtonStyle.danger, custom_id="apagar"))

# Evento: el bot está listo
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# Evento: mensaje recibido
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"DEBUG: Mensaje recibido: '{message.content}' de '{message.author.name}' en el canal '{message.channel.name}'")
    await bot.process_commands(message)

# Comando: enviar panel con botones
@bot.command(name="panel")
async def panel(ctx):
    print("Comando !panel ejecutado")
    await ctx.send("Controla la lámpara con los botones:", view=ControlLuzView())

# Evento: interacción con botones
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"] == "encender":
        mqtt_client.publish(MQTT_TOPIC, "ON")
        await interaction.response.send_message("Comando enviado: Encender", ephemeral=True)
    elif interaction.data["custom_id"] == "apagar":
        mqtt_client.publish(MQTT_TOPIC, "OFF")
        await interaction.response.send_message("Comando enviado: Apagar", ephemeral=True)

# Ejecutar el bot
bot.run(os.getenv("DISCORD_TOKEN"))
