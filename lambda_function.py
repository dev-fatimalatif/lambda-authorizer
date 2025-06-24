import os
import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode

# Environment variables
AWS_REGION = "us-xxxx-1"
COGNITO_USER_POOL_ID = "us-east-1_xxxxxxxxxxxxx"
COGNITO_APP_CLIENT_ID = "35mddvfej3pxxxxxxxxxxxxxx"

# Cognito JWKS URL
keys_url = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json'

# Load JWKS on cold start
with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']


def lambda_handler(event, context):
    """
    Lambda handler to authorize users based on Cognito JWT validation.
    """
    print("Event:", event)

    try:
        # Extract the token from the event
        token = parse_token(event)
        if not token:
            raise Exception("Unauthorized: Missing or invalid authorization token")

        # Validate the token
        claims = validate_token(token)
        print("Token is valid. Claims:", claims)

        # Check if user is in the 'admin' group
        if "admin" not in claims.get("cognito:groups", []):
            raise Exception("Unauthorized: User is not in the 'admin' group")

        # Generate an Allow policy for the user
        return get_allow_policy(claims['sub'], event['methodArn'])

    except Exception as e:
        print(f"Error during token validation: {e}")
        return get_deny_policy()


def parse_token(event):
    """
    Extract the JWT token from the 'authorizationToken' field in the event.
    """
    auth_token = event.get('authorizationToken', '')
    return auth_token if auth_token else None


def validate_token(token):
    """
    Validate the Cognito JWT token using the public keys.
    """
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']

    # Find the corresponding key in JWKS
    key_index = next((i for i, key in enumerate(keys) if key['kid'] == kid), -1)
    if key_index == -1:
        raise Exception('Public key not found in jwks.json')

    # Construct the public key
    public_key = jwk.construct(keys[key_index])

    # Verify the signature
    message, encoded_signature = token.rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    if not public_key.verify(message.encode("utf-8"), decoded_signature):
        raise Exception('Signature verification failed')

    # Decode and validate claims
    claims = jwt.get_unverified_claims(token)
    if time.time() > claims['exp']:
        raise Exception('Token is expired')

    if claims.get('aud') != COGNITO_APP_CLIENT_ID:
        raise Exception('Token was not issued for this audience')

    return claims


def get_allow_policy(principal_id, method_arn):
    """
    Generate an IAM policy to allow access.
    """
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": method_arn
                }
            ]
        }
    }


def get_deny_policy():
    """
    Generate a default Deny policy.
    """
    return {
        "principalId": "yyyyyyyy",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": "arn:aws:execute-api:*:*:*/ANY/*"
                }
            ]
        }
    }
