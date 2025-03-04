import discord
from utils.init_tribute import init_tribute
class TributeSetupFlow(discord.ui.View):
    def __init__(self, game_id):
        super().__init__(timeout=604800) # Seven days
        self.game_id = game_id

    @discord.ui.button(label="Identify", style=discord.ButtonStyle.green)
    async def setup_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        modal = TributeSetupModal(title="Identity")
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        init_tribute(
            user=interaction.user,
            guild=interaction.guild,
            game_id=self.game_id,
            nickname=modal.nickname,
            pronouns=modal.pronouns
        )
        await interaction.followup.send("Your identity has been confirmed. Happy Hunger Games, and may the odds be *ever* in your favor.")

class TributeSetupModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.nickname = None
        self.pronouns = None

        self.add_item(discord.ui.InputText(label="Nickname", placeholder="Enter the name you wish to be called."))
        self.add_item(discord.ui.InputText(label="Pronouns: Subject/Object/Posessive", placeholder='''EX: he/him/his'''))
    
    async def callback(self, interaction: discord.Interaction):
        self.nickname = self.children[0].value
        self.pronouns = self.children[1].value
        
        await interaction.response.defer(ephemeral=True)
        self.stop()