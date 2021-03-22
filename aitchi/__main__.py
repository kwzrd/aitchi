from aitchi.aitchi import Aitchi
from aitchi.config import Env

bot_instance = Aitchi(Env.prefix)

bot_instance.run(Env.token)
