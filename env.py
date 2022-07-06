import os
from dotenv import load_dotenv

load_dotenv()

env_vars = {
    'PORT': os.getenv('PORT', 5000),
    'SMB_PHOTO_LOCATION': os.getenv('SMB_PHOTO_LOCATION', os.path.join(os.getcwd(), 'photos'))
}
