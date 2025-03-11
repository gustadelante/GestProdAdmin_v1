import bcrypt
import json
import os

def verify_password(stored_hash, password):
    """Verify if the password matches the stored hash"""
    password_bytes = password.encode('utf-8')
    stored_hash_bytes = stored_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, stored_hash_bytes)

# Read existing credentials
creds_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credenciales.enc')
with open(creds_file, 'r') as f:
    credentials = json.load(f)

# Check if "op" user exists
if "op" in credentials:
    # Verify the password
    is_valid = verify_password(credentials["op"], "op")
    if is_valid:
        print("User 'op' with password 'op' can be accessed successfully!")
    else:
        print("Password 'op' does not match the stored hash for user 'op'")
else:
    print("User 'op' does not exist in the credentials file")