import requests

class PastebinClient:
    API_URL = "https://pastebin.com/api/api_post.php"

    @staticmethod
    def publish(api_key: str, content: str, privacy: int = 1, name: str = "FlashPaste Snippet") -> str:
        """
        Publishes content to Pastebin.
        privacy: 0=Public, 1=Unlisted, 2=Private
        Returns the URL of the paste.
        Raises requests.exceptions.RequestException on failure or API error.
        """
        if not api_key:
            raise ValueError("API Key is required")

        data = {
            'api_dev_key': api_key,
            'api_option': 'paste',
            'api_paste_code': content,
            'api_paste_private': privacy,
            'api_paste_name': name,
            'api_paste_expire_date': 'N', # Never expire on pastebin side implicitly, user manages it
        }

        try:
            response = requests.post(PastebinClient.API_URL, data=data, timeout=10)
            response.raise_for_status()
            
            # Pastebin returns the URL on success, or an error string starting with "Bad API Request"
            text = response.text.strip()
            if text.startswith("Bad API Request"):
                raise requests.exceptions.HTTPError(f"Pastebin API Error: {text}")
                
            return text
        except requests.RequestException as e:
            raise e
