import os
import requests
from core.config import get_config
from core.logger import get_logger

logger = get_logger("storage")
config = get_config()

def sync_to_cloud(filename, data):
    # Беремо URL та USER з конфігу або оточення
    url = config.get("CIT_WEBDAV_URL") or os.getenv("CIT_WEBDAV_URL")
    user = config.get("CIT_WEBDAV_USER") or os.getenv("CIT_WEBDAV_USER")
    # Пароль беремо з WEBDAV_PASSWORD
    password = os.getenv("WEBDAV_PASSWORD")
    
    if not all([url, user, password]):
        logger.warning(f"WebDAV sync skipped: missing credentials (URL: {bool(url)}, User: {bool(user)}, Pass: {bool(password)})")
        return False

    target_url = f"{url.rstrip('/')}/{filename}"
    try:
        logger.info(f"Syncing {filename} to WebDAV...")
        resp = requests.put(target_url, data=data, auth=(user, password), timeout=30)
        if resp.status_code in [201, 204]:
            logger.info(f"✅ Successfully synced to cloud: {filename}")
            return True
        else:
            logger.error(f"❌ WebDAV error {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Cloud sync exception: {e}")
        return False
