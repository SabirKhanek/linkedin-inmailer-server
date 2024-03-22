from linkedin_api import Linkedin

class LinkedInClientStore:
    _clients: dict[str, Linkedin] = {}

    def register_client(self, username: str, client: Linkedin):
        self._clients[username] = client

    def get_client(self, username: str):
        return self._clients.get(username)        
