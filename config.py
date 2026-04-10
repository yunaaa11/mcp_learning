import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    API_KEY=os.getenv("API_KEY")
    Model=os.getenv("Model")
    Base_url=os.getenv("Base_url")
    AMAP_KEY=os.getenv("AMAP_KEY")