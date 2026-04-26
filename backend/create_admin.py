from database import users_collection
def create_super_admin():
    admin_data = {
        "username": "admin@agrichain.com",
        "password": "adminpassword123", # Note: If your login uses hashed passwords, hash this first!
        "role": "Admin", 
        "name": "AgriChain Super Admin",
        "mobile": "9999999999"
    }
    existing_admin = users_collection.find_one({"username": "admin@agrichain.com"})
    if not existing_admin:
        users_collection.insert_one(admin_data)
        print("Admin user 'admin@agrichain.com' created successfully!")
    else:
        print("Admin user already exists.")
if __name__ == "__main__":
    create_super_admin()