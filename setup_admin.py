import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import FirebaseDB
from backend.models import User

def setup_admin():
    """Create an admin user"""
    try:
        db = FirebaseDB()
        
        admin_email = "bloodbanka485@gmail.com"
        admin_password = "blood123"
        
        # Create admin user
        admin_user = User(
            name="System Administrator",
            email=admin_email,
            contact_number="+1234567890",
            blood_group="O+",
            location="Headquarters",
            user_type="admin"
        )
        
        # Create auth user
        auth_user = db.create_user(admin_email, admin_password, admin_user.name)
        
        # Save user data
        db.save_user_data(auth_user['uid'], admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("Please login and change the password!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    setup_admin()