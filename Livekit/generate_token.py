import os
from livekit import api

# Define API Key and Secret (use defaults for local dev)
API_KEY = "devkey"
API_SECRET = "secret"

# Create a token with permissions to join a room
token = api.AccessToken(API_KEY, API_SECRET) \
    .with_identity("human-user") \
    .with_name("Human") \
    .with_grants(api.VideoGrants(
        room_join=True,
        room="test-room",
    ))

print(f"Token: {token.to_jwt()}")
