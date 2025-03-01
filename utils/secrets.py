from decouple import config, RepositoryEnv, Config
config = Config(RepositoryEnv('secrets.env'))
# API_KEY = config('API_KEY')
# MODEL = config('MODEL')
BOT_TOKEN = config('BOT_TOKEN')