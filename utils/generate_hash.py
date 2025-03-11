import bcrypt
import json
import os

def generate_password_hash(password):
    """Generate a bcrypt hash for the given password"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

# Generate hash for "op" password
op_hash = generate_password_hash("op")
print(f"Hash for 'op': {op_hash}")

# Read existing credentials
creds_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credenciales.enc')
with open(creds_file, 'r') as f:
    credentials = json.load(f)

# Add new user
credentials["op"] = op_hash

# Save updated credentials
with open(creds_file, 'w') as f:
    json.dump(credentials, f)

print("Credentials updated successfully!")