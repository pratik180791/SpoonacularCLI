from collections import namedtuple

KeyAuthenticator = namedtuple("KeyAuthenticator", ["url", "email", "password"], defaults=[None, None, None])


class AuthenticationHandler:
    def __init__(self, config = KeyAuthenticator(None, None, None)):
        """
        :param config: Provision to provide an object with credentials needed to key/tokens perform authentication etc
        """
        self.config = config

    def api_key(self) -> str:
        if not self.config.url:
            return "9313ebe82da444d488cde9008f07d7a4"
        return self.get_token()

    def get_token(self) -> str:
        """
        This is a placeholder to interact with service and get keys/tokens for authentication based on configs provided
        :return:
        """
        if not self.config.url and not self.config.password and not self.config.email:
            return "NOT IMPLEMENTED"
