import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from helpers.jwt_key_service import PublicKeyCache


class SSOBusinessTokenAuthentication(BaseAuthentication):
    """
    Authenticate Business users using JWT from Auth server.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split("Bearer ")[1]

        try:
            key_info = PublicKeyCache.get_public_key()
            secret_key = key_info["key"]
            algorithm = key_info["algorithm"]
            
            # Decode JWT without verifying audience (you can add it later if needed)
            decoded = jwt.decode(
                token,
                secret_key,
                algorithms=[algorithm],
            )

            # Only allow business user type
            if decoded.get("usertype") != "business":
                raise AuthenticationFailed("Invalid token type for Business user.")

            # Return a user-like object for DRF
            user = AuthenticatedBusinessUser(
                id=decoded.get("id"),
                user_id=decoded.get("user_id"),
                name=decoded.get("name"),
                business_id=decoded.get("business_id"),
                business_name=decoded.get("business_name"),
            )
            return (user, None)

        except ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except InvalidTokenError:
            raise AuthenticationFailed("Invalid or tampered token.")
        except Exception as e:
            raise AuthenticationFailed(f"Token verification failed: {e}")


class AuthenticatedBusinessUser:
    """
    Simple user object for DRF to represent an authenticated business user.
    """
    def __init__(self, id, user_id, name, business_id=None, business_name=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.business_id = business_id
        self.business_name = business_name

    @property
    def is_authenticated(self):
        return True