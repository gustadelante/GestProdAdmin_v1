import bcrypt
import json
import os

def generate_password_hash(password):
    """Generate a bcrypt hash for the given password"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

# Read existing credentials
creds_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credenciales.enc')
with open(creds_file, 'r') as f:
    credentials = json.load(f)

# Update or add user "op" with password "op"
op_hash = generate_password_hash("op")
credentials["op"] = op_hash

# Save updated credentials
with open(creds_file, 'w') as f:
    json.dump(credentials, f)

print("User 'op' updated with password 'op'")

# Verify the password
def verify_password(stored_hash, password):
    """Verify if the password matches the stored hash"""
    password_bytes = password.encode('utf-8')
    stored_hash_bytes = stored_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, stored_hash_bytes)

# Check if the password works
is_valid = verify_password(credentials["op"], "op")
if is_valid:
    print("Verification successful: User 'op' with password 'op' can be accessed!")
else:
    print("Verification failed: Password 'op' does not match the stored hash for user 'op'")