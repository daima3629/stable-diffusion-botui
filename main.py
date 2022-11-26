import discord
from discord import app_commands
import os
import aiohttp
import io
import base64
import json


class StableDiffusionBotUI(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SERVER_URL = os.getenv("SERVER_URL")
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()
        async with aiohttp.ClientSession(base_url=self.SERVER_URL) as session:
            r = await session.get("/sdapi/v1/sd-models")
            result = await r.json()
        self.model_data = result

    async def on_ready(self):
        print(f"Logged in as {self.user}")


intents = discord.Intents.default()
intents.typing = False

client = StableDiffusionBotUI(intents=intents)


@client.tree.command()
@app_commands.describe(
    prompt="画像情報を指示するテキスト",
    negative_prompt="画像に不要な情報を排除するためのテキスト",
    width="画像の横幅(デフォルト512)",
    height="画像の縦幅(デフォルト512)",
    seed="画像生成のシード",
    model="使用するモデル"
)
@app_commands.choices(
    model=[app_commands.Choice(name=d["model_name"], value=d["title"])
           for d in client.model_data]
)
async def generate(interaction: discord.Interaction, prompt: str, negative_prompt: str, model: app_commands.Choice[str], width=512, height=512, seed=-1):
    await interaction.response.defer()

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "seed": seed,
        "override_settings": {
            "sd_model_checkpoint": model
        }
    }

    async with aiohttp.ClientSession(base_url=client.SERVER_URL) as session:
        r = await session.post("/sdapi/v1/txt2img", json=payload)
        response = await r.json()

    image = io.BytesIO(base64.b64decode(response["images"][0].split(",",1)[0]))
    info = json.loads(response["info"])

    file = discord.File(fp=image, filename="output.png")
    embed = discord.Embed().set_image(url="attachment://output.png")
    embed.add_field(
        name="Info", 
        value=f"prompt: `{info['prompt']}`\n"
              f"negative prompt: `{info['negative_prompt']}`\n"
              f"width: `{info['width']}`\n"
              f"height: `{info['height']}`\n"
              f"seed: `{info['seed']}`"
              f"model: `{model}`"
    )
    await interaction.followup.send(embed=embed, file=file)

