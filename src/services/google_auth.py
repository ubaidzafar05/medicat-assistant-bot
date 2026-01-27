from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from src.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

class GoogleAuth:
    def __init__(self, app=None):
        self.config = Config(environ={'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET})
        self.oauth = OAuth(self.config)
        self.oauth.register(
            name='google',
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )
    
    def get_oauth(self):
        return self.oauth
