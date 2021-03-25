from aitchi.aitchi import Aitchi
from aitchi.config import Env

bot_instance = Aitchi()

bot_instance.load_extension("aitchi.extensions.tiktok")

bot_instance.run(Env.token)
