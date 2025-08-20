from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os
from dotenv import load_dotenv
import json
from urllib.parse import quote
import requests

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

AES_KEY_HEX = os.getenv('AES_ENCRYPTION_KEY')
AES_IV_HEX = os.getenv('AES_ENCRYPTION_IV')

KEY = bytes.fromhex(AES_KEY_HEX)
IV = bytes.fromhex(AES_IV_HEX)

def encrypt_response(plain_text: str) -> str:
    try:
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        encrypted_bytes = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    except Exception as e:
        print(f"encrypt_response Exception: {e}")
        return False
    
# result = encrypt_response(plain_text="""{"userId": "dEd5Y3RNVkVhajh0TWxDanBzWkFpQT09", "notes": "mi"}""")
# print(result)


def decrypt_data(encrypted_text: str) -> str:
    try:
        encrypted_bytes = base64.b64decode(encrypted_text)
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"decrypt_data Exception: {e}")
        return False

# result = decrypt_data(encrypted_text="ALNJa8IfeMc4937zj1RMzKb8+840b71pGDPO58SRZZkcneYuj7pGfJ+1nvFbJTrG4F8/OQ52gZjb+ZGsFo0i4A==")
# print(result)

def make_request(endpoint_name: str, data) -> dict[str, object]:
    """
    make request to get actual response for all the tools
    """
    # BASE_URL = "https://apiv6.goqii.com/carenavigator"
    url = BASE_URL + endpoint_name
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Ymt4NjFteVRYSytSZzE4NXFLV0FQUnVVM1VoZjh4Q3FLdlUzbi9vTVFXd1pEM2ZKUzJMNGhieERtZTZlNDZTYWs2WTFjTDQ4VVVSemRGcEJWam5jaS93d04rZHE5M0w3YUlBWnRJSUMwVHFsUWRwWlh4bjVRcWhvYnZNN0VHV2FqWVFJSDEvdnRYREtDZjd0SWFHYnc5VUNEcC9wUnEzakNiUkZIMGlQMTRYWTRIcU54cnUyclhVMEZDQ0MvK0JHMis1T0RqWGF6aHZORTF6ampyYnMzTXpiSDVzSldaV2d1MGZDeEpKb1QyWnRuemMzVVNhakVWdGFsVHk2eE5aR0lkL0NRSnE1WGJidVVrc09OU0E5TWk0dUN1NzNxUUNnOHdtR0dScWl6YlE9"
    }

    json_str = json.dumps(data)
    encrypted = encrypt_response(json_str)
    encoded = quote(encrypted, safe='')

    payload = {
        "encParams": encoded
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        res.raise_for_status()
        # print("Raw encrypted response:", res.text)

        decrypted = decrypt_data(res.text)
        # print("Decrypted JSON string:", decrypted)
        return json.loads(decrypted)
    
    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        return {"error": str(e)}
    
    except json.JSONDecodeError as e:
        # print("Decryption failed or invalid JSON:", e)
        return {"error": "Invalid JSON from decrypted response", "raw": decrypted}