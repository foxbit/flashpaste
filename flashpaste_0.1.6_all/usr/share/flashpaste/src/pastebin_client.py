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

        api_key = api_key.strip()
        
        # Ensure headers to avoid blocking
        headers = {
            'User-Agent': 'FlashPaste/0.1.5 (Linux)'
        }

        data = {
            'api_dev_key': api_key,
            'api_option': 'paste',
            'api_paste_code': content,
            'api_paste_private': privacy if privacy != 2 else 1, # Downgrade Private to Unlisted
            'api_paste_name': name,
            'api_paste_expire_date': 'N',
            'api_user_key': '', # Explicitly empty for guest paste
        }
        
        print(f"DEBUG: Publishing with Key='{api_key[:5]}...' len={len(content)} privacy={data['api_paste_private']}")

        try:
            response = requests.post(PastebinClient.API_URL, data=data, headers=headers, timeout=15)
            
            # Print response for debugging
            print(f"DEBUG: Status={response.status_code} Body={response.text[:100]}")
            
            response.raise_for_status()
            
            # Pastebin returns the URL on success, or an error string starting with "Bad API Request"
            text = response.text.strip()
            if text.startswith("Bad API Request"):
                raise requests.exceptions.HTTPError(f"Pastebin API Error: {text}")
                
            return text
        except requests.RequestException as e:
            raise e
