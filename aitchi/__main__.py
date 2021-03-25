from aitchi.aitchi import Aitchi
from aitchi.config import Secrets

bot_instance = Aitchi()

bot_instance.load_extension("aitchi.extensions.tiktok")

bot_instance.run(Secrets.bot_token)
