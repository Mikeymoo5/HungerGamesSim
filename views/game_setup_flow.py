import discord
class GameModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(timeout=300) # 5 Minutes
    
        self.add_item(discord.ui.InputText(label="#th Hunger Game", placeholder="EX: 7 = 7th annual hunger games"))
        self.add_item(discord.ui.InputText(label="Arena Description", placeholder="Enter what you want the arena to be like",style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        self.num = self.children[0].value
        self.description = self.children[1].value
        