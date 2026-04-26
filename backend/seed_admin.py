from database import users_collection
from security import get_password_hash

def reset_master_admin():
    admin_email = "admin@agrichain.com"
    admin_password = "Admin123"
    print(f"🧹 Deleting any old corrupted admin accounts...")
    users_collection.delete_many({"username": admin_email})
    print("🔒 Generating secure password hash...")
    hashed_pw = get_password_hash(admin_password)
    print(f"Hash preview: {hashed_pw[:15]}...") 
    admin_user = {
        "username": admin_email,
        "password": hashed_pw,
        "role": "admin"
    }
    users_collection.insert_one(admin_user)
    print("Master Admin account recreated with a secure hash!")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")

if __name__ == "__main__":
    reset_master_admin()