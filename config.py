import os

class Config:
    API_ID = int(os.environ.get("API_ID", 38138069))
    API_HASH = os.environ.get("API_HASH", "2ed313ebcc45cbcf65d1fc736ec71681")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8898176097:AAEp_YmuAsLuEOsvgySpT9BgF_EOMOGdNDU")
    MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://Nova:novacoder76@cluster0.njvqq11.mongodb.net/?appName=Cluster0")
    
    START_IMG = "https://files.catbox.moe/bpktqb.jpg"
    BOT_USERNAME = "Group_secu_bot"
    UPDATE_CH = "MoviesHub_Verse"
    
    PORT = int(os.environ.get("PORT", 8080))

