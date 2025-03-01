import discord
class GameFlow(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=3)

    @discord.ui.button(label="Identify", style=discord.ButtonStyle.green)
    async def setup_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        modal = GameFlowModal(title="Identity")
        await interaction.response.send_modal(modal)

class GameFlowModal(discord.ui.Modal):
    def _init_(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.nickname: str = None
        self.pronouns: str = None

        self.add_item(discord.ui.InputText(label="Nickname", placeholder="Enter the name you wish to be called."))
        self.add_item(discord.ui.InputText(label="Pronouns", placeholder="Please enter the pronouns you want the bot to use."))
    
    async def callback(self, interaction: discord.Interaction):
        self.nickname = self.children[0].value
        self.pronouns = self.children[1].value
        await interaction.response.defer(ephemeral=True)

        self.stop()