import discord
from discord import app_commands
import os
import aiohttp
import io
import base64
import json
import requests
import asyncio
from typing import Tuple

import dotenv
dotenv.load_dotenv()


class StableDiffusionBotUI(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SERVER_URL = os.getenv("SERVER_URL")
        self.tree = app_commands.CommandTree(self)

        res = requests.get(self.SERVER_URL+"/sdapi/v1/sd-models")
        self.model_data = res.json()

        self.queue: asyncio.Queue[Tuple[discord.Interaction, dict, app_commands.Choice[str]]] = asyncio.Queue()

    async def on_ready(self):
        await self.tree.sync()
        print(f"Logged in as {self.user}")
        self.loop.create_task(self.generation_loop())

    async def generation_loop(self):
        while True:
            interaction, payload, model = await self.queue.get()
            await interaction.edit_original_response(embed=discord.Embed(description="生成が開始されました。しばらくお待ちください…"))

            async with aiohttp.ClientSession(base_url=self.SERVER_URL) as session:
                r = await session.post("/sdapi/v1/txt2img", json=payload)
                response = await r.json()

            image = io.BytesIO(base64.b64decode(response["images"][0].split(",",1)[0]))
            info = json.loads(response["info"])

            file = discord.File(fp=image, filename="output.png")
            embed = discord.Embed().set_image(url="attachment://output.png")
            embed.add_field(
                name="Info", 
                value=f"prompt: `{info['prompt']}`\n"
                    f"negative prompt: `{info['negative_prompt'] if info['negative_prompt'] else 'なし'}`\n"
                    f"width: `{info['width']}`\n"
                    f"height: `{info['height']}`\n"
                    f"seed: `{info['seed']}`\n"
                    f"model: `{model.name}`"
            )
            await interaction.edit_original_response(embed=embed, attachments=[file])


intents = discord.Intents.default()
intents.typing = False

client = StableDiffusionBotUI(intents=intents)


@client.tree.command(description="画像を生成します")
@app_commands.describe(
    prompt="画像情報を指示するテキスト",
    model="使用するモデル",
    nsfw="NSFW画像を生成しようとしているか",
    negative_prompt="画像に不要な情報を排除するためのテキスト",
    seed="画像生成のシード",
)
@app_commands.choices(
    model=[app_commands.Choice(name=d["model_name"], value=d["title"])
           for d in client.model_data]
)
async def generate(interaction: discord.Interaction, prompt: str, model: app_commands.Choice[str], nsfw: bool, negative_prompt: str = "", seed: int = -1):

    if interaction.guild is not None:
        if nsfw is True:
            if (interaction.channel.type is not discord.ChannelType.text) or interaction.channel.nsfw is not True:
                await interaction.response.send_message(embed=discord.Embed(description="NSFWコンテンツはNSFWチャンネル以外では生成できません！", color=discord.Colour.red()))
                return

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "seed": seed,
        "override_settings": {
            "sd_model_checkpoint": model.value
        }
    }

    await interaction.response.send_message(embed=discord.Embed(description="キューされました。生成が開始されるまでお待ち下さい…"))
    await client.queue.put((interaction, payload, model))


client.run(os.getenv("DISCORD_TOKEN"))
