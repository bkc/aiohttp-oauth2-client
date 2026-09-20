from typing import Optional, Union
import enum
import base64

from yarl import URL

from aiohttp_oauth2_client.grant.common import OAuth2Grant
from aiohttp_oauth2_client.models.request import ClientCredentialsAccessTokenRequest
from aiohttp_oauth2_client.models.token import Token


class CredentialsSendLocation(str, enum.Enum):
    """Enum for the location to send client credentials in the request."""

    HEADER = "header"
    """Send client credentials in the Authorization header."""

    BODY = "body"
    """Send client credentials in the request body."""


class ClientCredentialsGrant(OAuth2Grant):
    """
    OAuth 2.0 Client Credentials grant.

    Use client credentials to obtain an access token.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.4
    """

    def __init__(
        self,
        token_url: Union[str, URL],
        client_id: str,
        client_secret: str,
        token: Optional[dict] = None,
        credentials_send_location: CredentialsSendLocation = CredentialsSendLocation.BODY,
        **kwargs,
    ):
        """

        :param token_url: OAuth 2.0 Token URL
        :param client_id: client identifier
        :param client_secret: client secret
        :param token: OAuth 2.0 Token
        :param credentials_send_location: location to send client credentials (header or body)
        """
        super().__init__(token_url, token, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = None
        if credentials_send_location == CredentialsSendLocation.HEADER:
            self.headers = {
                "Authorization": f"Basic {self._encode_client_credentials()}"
            }

    def _encode_client_credentials(self) -> str:
        credentials = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(credentials.encode()).decode()

    async def _fetch_token(self) -> Token:
        access_token_request = ClientCredentialsAccessTokenRequest(
            client_id=self.client_id, client_secret=self.client_secret, **self.kwargs
        )
        return await self.execute_token_request(
            access_token_request, headers=self.headers
        )

    async def refresh_token(self):
        """
        Following the specification, the token response for the client credentials grant SHOULD NOT include a refresh token.
        The client credentials grant should be used to get a new access token when the previous one has expired.

        https://datatracker.ietf.org/doc/html/rfc6749#section-4.4.3

        Some clients may issue a refresh token for the client credentials flow, even though it is not correct according to the specification.
        In this case, the refresh token will be used to obtain a new access token.
        """
        if "refresh_token" in self.token:
            # use refresh token when it is available
            await super().refresh_token(headers=self.headers)

        # just get a new token using the client credentials
        await self.fetch_token()
