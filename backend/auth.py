from typing import Dict
from .database import FirebaseDB
from .models import User

class AuthManager:
    def __init__(self):
        self.db = FirebaseDB()
        self.current_user = None
        self.current_user_id = None
    
    def signup(self, user_data: User, password: str) -> bool:
        """Register a new user"""
        try:
            # Create authentication user
            auth_user = self.db.create_user(user_data.email, password, user_data.name)
            
            # Save user data to database
            self.db.save_user_data(auth_user['uid'], user_data)
            
            return True
        except Exception as e:
            raise e
    
    def login(self, email: str, password: str) -> Dict:
        """Login user and get user data"""
        try:
            print(f"🔐 AuthManager.login called for: {email}")
            
            # Use the proper login_user method that verifies password
            user_info = self.db.login_user(email, password)
            
            print(f"✅ AuthManager received user_info")
            print(f"   Keys in user_info: {user_info.keys()}")
            print(f"   Has user_data: {'user_data' in user_info}")
            
            if not user_info or 'user_data' not in user_info:
                raise Exception("User data not found in response")
            
            # Store current user info
            self.current_user = user_info['user_data']
            self.current_user_id = user_info['user_id']
            
            print(f"✅ AuthManager.login successful")
            print(f"   User ID: {self.current_user_id}")
            print(f"   User name: {self.current_user.get('name', 'Unknown')}")
            
            return user_info
            
        except Exception as e:
            print(f"❌ AuthManager.login failed: {e}")
            raise e
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.current_user_id = None
    
    def is_admin(self, user_data: Dict) -> bool:
        """Check if user is admin"""
        return user_data.get('user_type') == 'admin'
    
    def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        return self.db.reset_password(email)