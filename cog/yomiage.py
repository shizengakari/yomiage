import discord
from discord.ext import commands
from discord import app_commands
import edge_tts
import asyncio
import json
import os

class Yomiage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.settings = {}
        self.load_settings()
        self.voice_queues = {}
        self.is_playing = {}

    def load_settings(self):
        try:
            with open('yomiage_settings.json', 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}

    def save_settings(self):
        with open('yomiage_settings.json', 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)

    def get_server_settings(self, guild_id):
        str_guild_id = str(guild_id)
        if str_guild_id not in self.settings:
            self.settings[str_guild_id] = {
                'volume': 0.1,
                'voice': 'ja-JP-NanamiNeural',
                'speed': 1.0
            }
        return self.settings[str_guild_id]

    @app_commands.command(name="join", description="ボイスチャンネルに参加")
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("先にボイスチャンネルに参加してください。", ephemeral=True)
            return
        
        await interaction.user.voice.channel.connect()
        await interaction.response.send_message("接続しました。")

    @app_commands.command(name="leave", description="ボイスチャンネルから退出")
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("切断しました。")
        else:
            await interaction.response.send_message("ボイスチャンネルに接続していません。")

    @app_commands.command(name="volume", description="音量を設定")
    async def set_volume(self, interaction: discord.Interaction, volume: float):
        if not 0.1 <= volume <= 2.0:
            await interaction.response.send_message("音量は0.1から2.0の間で指定してください。")
            return

        settings = self.get_server_settings(interaction.guild_id)
        settings['volume'] = volume
        self.save_settings()
        await interaction.response.send_message(f"音量を{volume}に設定しました。")

    async def generate_speech(self, text, guild_id):
        settings = self.get_server_settings(guild_id)
        wav_path = f"temp_{guild_id}.wav"
        
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=settings.get('voice', 'ja-JP-NanamiNeural'),
                rate=f"{settings.get('speed', 1.0)}x"
            )
            await communicate.save(wav_path)
            return wav_path
        except Exception as e:
            print(f"Speech generation error: {e}")
            return None

    async def speak_text(self, text, guild):
        if not guild.voice_client:
            return

        wav_path = await self.generate_speech(text, guild.id)
        if not wav_path:
            return

        try:
            source = discord.FFmpegPCMAudio(wav_path)
            guild.voice_client.play(
                discord.PCMVolumeTransformer(
                    source,
                    volume=self.get_server_settings(guild.id)['volume']
                ),
                after=lambda e: os.remove(wav_path) if os.path.exists(wav_path) else None
            )
        except Exception as e:
            print(f"Playback error: {e}")
            if os.path.exists(wav_path):
                os.remove(wav_path)

async def setup(bot):
    await bot.add_cog(Yomiage(bot))
