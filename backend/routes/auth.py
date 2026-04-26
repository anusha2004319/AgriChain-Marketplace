from fastapi import APIRouter, HTTPException, status
from backend.database import users_collection
from backend.security import verify_password, get_password_hash, create_access_token

# Import your exact schemas here!
from backend.schemas import UserAuth, UserLogin 

router = APIRouter()

# --- REGISTRATION ROUTE ---
@router.post("/register") # The /api prefix is automatically added by main.py
def register_user(user: UserAuth):
    # Check if the email (username) already exists
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    hashed_pw = get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = hashed_pw 
    
    users_collection.insert_one(user_dict)
    return {"status": "success", "message": "User registered successfully"}

# --- LOGIN ROUTE (JWT GENERATION) ---
@router.post("/login")
def login_user(credentials: UserLogin):
    # 1. Clean up inputs to ignore capitalization and accidental spaces
    clean_username = credentials.username.strip().lower()
    clean_role = credentials.role.strip().lower()
    print(f"\n--- 🔍 DEBUG LOGIN START ---")
    print(f"1. Frontend sent -> Username: '{credentials.username}', Password: '{credentials.password}', Role: '{credentials.role}'")
    print(f"2. Searching DB for -> Username: '{clean_username}', Role: '{clean_role}'")
    # 2. Find user by email and role (using the cleaned strings)
    user = users_collection.find_one({
        "username": clean_username, 
        "role": clean_role
    })
    print("\n--- FINAL DEBUG ---")
    print(f"Did DB find user? -> {user is not None}")
    if user:
        print(f"Is password valid? -> {verify_password(credentials.password, user['password'])}")
    print("-------------------\n")
    # 3. Check if user exists AND if the hashed password matches
    if not user or not verify_password(credentials.password, user["password"]):
        print(f"❌ Login Failed for {clean_username} as {clean_role}") # Helpful terminal debug
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password"
        )
    print("✅ RESULT: Login completely successful!")
    print("--- DEBUG END ---\n")
    print(f"✅ Login Success for {clean_username} as {clean_role}")

    # 4. Generate the JWT Token
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user["username"],
        "role": user["role"]
    }