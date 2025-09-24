from rest_framework_simplejwt.authentication import JWTAuthentication

class TokenUser:
    def __init__(self, user_id, role):
        self.id = user_id
        self.role = role

    @property
    def is_authenticated(self):
        return True
        

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        role = validated_token.get("role")

        if not user_id:
            return None  

        return TokenUser(user_id, role)
    