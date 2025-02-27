import requests
import os
import json
from cryptography.fernet import Fernet
from config.config import URL_BASE,ENCRYPTION_KEY_FILE,TOKEN_FILE  # Importing your BASE URL

class FacebookTokenManager:
    """
    Manages Facebook long-lived tokens securely.
    - Encrypts and stores tokens in a file.
    - Refreshes tokens when they expire.
    - Retrieves the stored token if valid.
    """

    ENCRYPTION_KEY_FILE = ENCRYPTION_KEY_FILE
    TOKEN_FILE = TOKEN_FILE

    def __init__(self, short_lived_token=None):
        self.short_lived_token = short_lived_token
        self.GRAPH_API_URL = f"{URL_BASE}oauth/access_token"  # Uses the imported BASE URL
        self._ensure_encryption_key()

    # 🔒 Step 1: Generate Encryption Key (Only if not exist)
    def _ensure_encryption_key(self):
        """Ensures that the encryption key file exists."""
        directory = os.path.dirname(self.ENCRYPTION_KEY_FILE)  # Extract directory path
        os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist

        if not os.path.exists(self.ENCRYPTION_KEY_FILE):
            key = Fernet.generate_key()
            with open(self.ENCRYPTION_KEY_FILE, "wb") as key_file:
                key_file.write(key)
            print("✅ Encryption key generated and saved securely.")

    # 🔑 Step 2: Load Encryption Key
    def _load_encryption_key(self):
        """Loads the encryption key from file."""
        with open(self.ENCRYPTION_KEY_FILE, "rb") as key_file:
            return key_file.read()

    # 🔒 Step 3: Encrypt Data Before Saving
    def _encrypt_data(self, data):
        """Encrypts data using the stored encryption key."""
        cipher = Fernet(self._load_encryption_key())
        return cipher.encrypt(data.encode()).decode()

    # 🔓 Step 4: Decrypt Data When Loading
    def _decrypt_data(self, data):
        """Decrypts data using the stored encryption key."""
        cipher = Fernet(self._load_encryption_key())
        return cipher.decrypt(data.encode()).decode()

    # 🔄 Step 5: Save Token Securely
    def _save_token(self, token):
        """Encrypts and stores the token securely."""
        encrypted_token = self._encrypt_data(token)
        with open(self.TOKEN_FILE, "w") as file:
            json.dump({"token": encrypted_token}, file)
        print("✅ Token securely saved.")

    # 📂 Step 6: Load Token from File
    def _load_token(self):
        """Loads the stored encrypted token and decrypts it."""
        if not os.path.exists(self.TOKEN_FILE):
            return None
        with open(self.TOKEN_FILE, "r") as file:
            data = json.load(file)
        return self._decrypt_data(data["token"])

    # 🔄 Step 7: Get a Long-Lived Token (First Time)
    def _get_long_lived_token(self):
        """Fetches a new long-lived token from the short-lived token."""

        # Load your App ID and App Secret from environment variables
        client_id = os.getenv("FB_APP_ID")
        client_secret = os.getenv("FB_APP_SECRET")

        if not client_id or not client_secret:
            raise ValueError("❌ FB_APP_ID and FB_APP_SECRET environment variables must be set!")

        params = {
            "grant_type": "fb_exchange_token",
            "client_id": client_id,  # Required
            "client_secret": client_secret,  # Required
            "fb_exchange_token": self.short_lived_token  # Short-lived token
        }

        response = requests.get(self.GRAPH_API_URL, params=params)

        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ New Long-Lived Token")
            return token
        else:
            raise requests.exceptions.RequestException(
                f"❌ Error fetching long-lived token: {response.status_code} - {response.text}"
            )

    # 🔄 Step 8: Refresh Token (Every 60 Days)
    def _refresh_token(self, long_lived_token):
        """Refreshes the stored long-lived token when it nears expiration."""

        refresh_url = f"https://graph.facebook.com/v22.0/oauth/access_token"  # Corrected URL

        params = {
            "grant_type": "fb_exchange_token",
            "client_id": os.getenv("FB_APP_ID"),  # Ensure these are correctly set
            "client_secret": os.getenv("FB_APP_SECRET"),
            "fb_exchange_token": long_lived_token
        }

        response = requests.get(refresh_url, params=params)

        if response.status_code == 200:
            new_token = response.json().get("access_token")
            print("✅ Refreshed Token")
            return new_token
        else:
            raise requests.exceptions.RequestException(
                f"❌ Error refreshing token: {response.status_code} - {response.text}"
            )

    # 🚀 Main Process: Manage Token Securely
    def get_token(self):
        """
        Returns a valid long-lived token.
        - If no token exists, fetch a new one.
        - If a token exists, refresh it when needed.
        """
        token = self._load_token()

        if not token:
            print("🔄 No saved token found. Fetching new long-lived token...")
            if not self.short_lived_token:
                raise ValueError("❌ No short-lived token provided. Cannot generate a new token.")
            token = self._get_long_lived_token()
            self._save_token(token)
        else:
            print("🔄 Existing token found. Refreshing...")
            token = self._refresh_token(token)
            self._save_token(token)

        return token
