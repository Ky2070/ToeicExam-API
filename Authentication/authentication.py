from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken


class SingleDeviceJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        # Skip JTI check for refresh tokens
        if validated_token.get("token_type") == "refresh":
            return user

        # Get the JTI from the token
        token_jti = validated_token.get("jti")

        # Check if the token's JTI matches the user's current_jti
        if user.current_jti and token_jti != user.current_jti:
            raise AuthenticationFailed("Token is no longer valid. Please log in again.")

        return user
