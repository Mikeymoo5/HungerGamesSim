import discord
from utils.init_guild import init_guild

class SetupFlow(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=180)  # 3 minutes in seconds
        self.gamemaker_role = None
        self.tribute_role = None
        self.announcement_channel = None
        self.user = user  # Store the user who initiated the command
    
    # This checks if the interaction user is the same as the one who started the command
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("Sorry, only the person who ran this command can use these controls.", ephemeral=True)
            return False
        return True

    @discord.ui.role_select(
        placeholder="Select a role for the Game Makers",
        min_values=1, max_values=1
    )
    async def game_maker_dropdown(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ) -> None:
        self.gamemaker_role = select.values[0]
        await interaction.response.defer(ephemeral=True)

    @discord.ui.role_select(
        placeholder="Select a role for the Tributes",
        min_values=1, max_values=1
    )
    async def tribute_dropdown(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ) -> None:
        self.tribute_role = select.values[0]
        await interaction.response.defer(ephemeral=True)

    @discord.ui.channel_select(
        placeholder="Select a channel for game announcements",
        min_values=1, max_values=1
    )
    async def announcement_dropdown(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ) -> None:
        self.announcement_channel = select.values[0]
        await interaction.response.defer(ephemeral=True)  # Acknowledge the interaction without sending a visible response

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        # Check if both selections were made
        if not self.gamemaker_role or not self.announcement_channel:
            await interaction.response.send_message("Please select both a role and a channel before continuing..", ephemeral=True)
            return
        
        modal = LLMModal(title="LLM Configuration")
        await interaction.response.send_modal(modal)
        await modal.wait()  # Wait until the modal is stopped
        print("ANNOUNCEMENT CHANNEL ID: " + str(self.announcement_channel.id))
        if modal.completed:
            init_guild(
                modal.api_key,
                modal.model_name,
                str(self.announcement_channel.id),
                str(self.gamemaker_role.id),
                str(self.tribute_role.id),
                interaction.guild
            )
            await interaction.followup.send("Guild initialized successfully!")
            self.stop()
        else:
            await interaction.followup.send("LLM setup was not completed. Please try again.", ephemeral=True)

class LLMModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.completed = False

        self.add_item(discord.ui.InputText(label="LLM Model", placeholder="Enter the model name here"))
        self.add_item(discord.ui.InputText(label="API Key", placeholder="Enter your API key here"))
    
    async def callback(self, interaction: discord.Interaction):
        self.model_name = self.children[0].value
        self.api_key = self.children[1].value
        self.completed = True
        await interaction.response.defer(ephemeral=True)

        self.stop()
    