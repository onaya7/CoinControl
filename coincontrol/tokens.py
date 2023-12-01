import os
from itsdangerous import URLSafeTimedSerializer
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(os.environ.get("SECRET_KEY"))
    return serializer.dumps(email, salt= os.environ.get("SECURITY_PASSWORD_SALT"))

def check_confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.environ.get("SECRET_KEY"))

    email = serializer.loads(
        token,
        salt =  os.environ.get("SECURITY_PASSWORD_SALT"),
        max_age=expiration
    )
 
    return email