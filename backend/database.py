import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin.exceptions import FirebaseError
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import os

class FirebaseDB:
    def __init__(self, 
                 service_account_file: str = "firebase_config.json",
                 web_config_file: str = "firebase_web_config.json"):
        try:
            print("Initializing FirebaseDB...")
            
            # Load Firebase web config for API key
            if os.path.exists(web_config_file):
                with open(web_config_file, 'r') as f:
                    web_config = json.load(f)
                self.api_key = web_config.get("apiKey", "")
                print(f"✅ Loaded API key from {web_config_file}")
            else:
                print(f"⚠️  {web_config_file} not found. Checking service account...")
                # Try to get API key from service account
                if os.path.exists(service_account_file):
                    with open(service_account_file, 'r') as f:
                        service_config = json.load(f)
                    self.api_key = service_config.get("apiKey", "")
                    
                    if not self.api_key:
                        # Try environment variable
                        self.api_key = os.environ.get("FIREBASE_API_KEY", "")
                        if self.api_key:
                            print("✅ Loaded API key from environment variable")
            
            if not self.api_key:
                raise Exception("Firebase API key not found. Please check firebase_web_config.json")
            
            print(f"✅ Using API key: {self.api_key[:15]}...")
            
            # Initialize Firebase Admin SDK
            if not firebase_admin._apps:
                print("✅ Initializing Firebase Admin SDK...")
                cred = credentials.Certificate(service_account_file)
                firebase_admin.initialize_app(cred)
            
            self.auth = auth
            self.db = firestore.client()
            print("✅ Firebase initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {str(e)}")
            raise
    
    # Authentication Methods
    def create_user(self, email: str, password: str, display_name: str = None) -> Dict:
        """Create a new user in Firebase Authentication"""
        try:
            print(f"Creating user: {email}")
            user = self.auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            print(f"✅ User created: {user.uid}")
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name
            }
        except FirebaseError as e:
            raise Exception(f"Error creating user: {str(e)}")
    
    def verify_password(self, email: str, password: str) -> Dict:
        """Verify email/password using Firebase REST API"""
        try:
            print(f"Verifying password for: {email}")
            
            if not self.api_key:
                raise Exception("API key not configured")
            
            # Firebase Authentication REST API endpoint
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            if response.status_code == 200:
                print(f"✅ Password verified for {email}")
                return {
                    'uid': result['localId'],
                    'email': result['email'],
                    'idToken': result['idToken'],
                    'refreshToken': result['refreshToken']
                }
            else:
                error_msg = result.get('error', {}).get('message', 'Authentication failed')
                # Make error messages more user-friendly
                if "INVALID_LOGIN_CREDENTIALS" in error_msg:
                    error_msg = "Invalid email or password"
                elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_msg:
                    error_msg = "Too many failed attempts. Please try again later."
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            raise Exception("Connection timeout. Please check your internet connection.")
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    def login_user(self, email: str, password: str) -> Dict:
        """Login user with proper password verification"""
        try:
            print(f"📧 Attempting login for: {email}")
            
            # Verify password using REST API
            auth_result = self.verify_password(email, password)
            print(f"✅ Password verified, user ID: {auth_result['uid']}")
            
            # Get user data from Firestore
            user_data = self.get_user_data(auth_result['uid'])
            print(f"🔍 User data from Firestore: {user_data}")
            
            if not user_data:
                print(f"⚠️  User data not found in Firestore, creating basic record...")
                # If user exists in auth but not in Firestore, create basic record
                user_data = {
                    'email': email,
                    'name': email.split('@')[0],
                    'contact_number': '',
                    'blood_group': '',
                    'location': '',
                    'user_type': 'user',
                    'created_at': datetime.now().isoformat()
                }
                
                # Save to Firestore
                self.save_user_data(auth_result['uid'], user_data)
                print(f"✅ Created basic user record in Firestore")
            
            print(f"✅ Login successful for {email}")
            print(f"   User type: {user_data.get('user_type', 'user')}")
            
            return {
                'user_id': auth_result['uid'],
                'user_data': user_data,
                'token': auth_result.get('idToken', '')
            }
            
        except Exception as e:
            print(f"❌ Login failed in login_user method: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Login failed: {str(e)}")
    
    def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        try:
            print(f"Generating password reset link for: {email}")
            
            # Generate password reset link
            reset_link = self.auth.generate_password_reset_link(
                email,
                action_code_settings=auth.ActionCodeSettings(
                    url='https://blood-bank-bda2f.firebaseapp.com',
                    handle_code_in_app=False
                )
            )
            
            print(f"✅ Password reset link generated: {reset_link[:50]}...")
            
            # Try to send email via SMTP if configured
            try:
                if os.path.exists('email_config.json'):
                    with open('email_config.json', 'r') as f:
                        email_config = json.load(f)
                    
                    import smtplib
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart
                    
                    msg = MIMEMultipart()
                    msg['From'] = email_config['sender_email']
                    msg['To'] = email
                    msg['Subject'] = "Blood Donation System - Password Reset"
                    
                    body = f"""
                    <html>
                    <body>
                        <h2>Password Reset Request</h2>
                        <p>You requested to reset your password for the Blood Donation System.</p>
                        <p>Click the link below to reset your password:</p>
                        <p><a href="{reset_link}">{reset_link}</a></p>
                        <p>This link will expire in 24 hours.</p>
                        <p>If you didn't request this, please ignore this email.</p>
                        <br>
                        <p>Best regards,<br>Blood Donation System Team</p>
                    </body>
                    </html>
                    """
                    
                    msg.attach(MIMEText(body, 'html'))
                    
                    with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                        if email_config.get('use_tls', True):
                            server.starttls()
                        server.login(email_config['sender_email'], email_config['sender_password'])
                        server.send_message(msg)
                    
                    print(f"✅ Password reset email sent to {email}")
                else:
                    print(f"⚠️  email_config.json not found. Link: {reset_link}")
            except Exception as email_error:
                print(f"⚠️  Could not send email: {email_error}")
                print(f"📋 Password reset link: {reset_link}")
            
            return True
                
        except FirebaseError as e:
            raise Exception(f"Password reset failed: {str(e)}")
    
    # User Data Methods
    def save_user_data(self, user_id: str, user_data) -> bool:
        """Save user data to Firestore"""
        try:
            if hasattr(user_data, '__dict__'):
                # It's a User object
                user_dict = user_data.__dict__.copy()
            else:
                # It's already a dict
                user_dict = user_data.copy()
            
            # Convert datetime to string if needed
            if 'created_at' in user_dict and not isinstance(user_dict['created_at'], str):
                user_dict['created_at'] = user_dict['created_at'].isoformat()
            
            # Save to Firestore
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.set(user_dict)
            print(f"✅ User data saved for {user_id}")
            return True
        except Exception as e:
            raise Exception(f"Error saving user data: {str(e)}")
    
    def get_user_data(self, user_id: str) -> Optional[Dict]:
        """Get user data by user ID"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Error getting user data: {str(e)}")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """Get all registered users"""
        try:
            users_ref = self.db.collection('users')
            docs = users_ref.stream()
            
            users = []
            for doc in docs:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                users.append(user_data)
            
            return users
        except Exception as e:
            print(f"Error getting all users: {str(e)}")
            return []
    
    def get_users_by_blood_group(self, blood_group: str) -> List[Dict]:
        """Get users by blood group"""
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where('blood_group', '==', blood_group)
            docs = query.stream()
            
            users = []
            for doc in docs:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                users.append(user_data)
            
            return users
        except Exception as e:
            print(f"Error filtering users: {str(e)}")
            return []
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user data"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.update(updates)
            return True
        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")
    
    # Post Methods
    def create_post(self, post) -> str:
        """Create a new donation post"""
        try:
            if hasattr(post, '__dict__'):
                # It's a Post object
                post_dict = post.__dict__.copy()
            else:
                # It's already a dict
                post_dict = post.copy()
            
            # Convert datetime to string if needed
            if 'created_at' in post_dict and not isinstance(post_dict['created_at'], str):
                post_dict['created_at'] = post_dict['created_at'].isoformat()
            
            # Add to Firestore
            doc_ref = self.db.collection('posts').document()
            doc_ref.set(post_dict)
            post_id = doc_ref.id
            print(f"✅ Post created with ID: {post_id}")
            return post_id
        except Exception as e:
            raise Exception(f"Error creating post: {str(e)}")
    
    def get_all_posts(self) -> List[Dict]:
        """Get all donation posts"""
        try:
            posts_ref = self.db.collection('posts')
            query = posts_ref.order_by('created_at', direction=firestore.Query.DESCENDING)
            docs = query.stream()
            
            posts = []
            for doc in docs:
                post_data = doc.to_dict()
                post_data['post_id'] = doc.id
                posts.append(post_data)
            
            return posts
        except Exception as e:
            print(f"Error getting posts: {str(e)}")
            return []
    
    def get_open_posts(self) -> List[Dict]:
        """Get all open donation posts"""
        try:
            posts_ref = self.db.collection('posts')
            query = posts_ref.where('status', '==', 'open').order_by('created_at', direction=firestore.Query.DESCENDING)
            docs = query.stream()
            
            posts = []
            for doc in docs:
                post_data = doc.to_dict()
                post_data['post_id'] = doc.id
                posts.append(post_data)
            
            return posts
        except Exception as e:
            print(f"Error getting open posts: {str(e)}")
            return []
    
    def update_post_status(self, post_id: str, status: str) -> bool:
        """Update post status"""
        try:
            doc_ref = self.db.collection('posts').document(post_id)
            doc_ref.update({'status': status})
            return True
        except Exception as e:
            raise Exception(f"Error updating post: {str(e)}")
        
    def get_user_posts(self, user_id: str) -> List[Dict]:
        """Get all posts by a specific user"""
        try:
            print(f"Getting posts for user: {user_id}")
            
            # Use simple query without ordering to avoid index requirement
            posts_ref = self.db.collection('posts')
            query = posts_ref.where('user_id', '==', user_id)
            docs = query.stream()
            
            posts = []
            for doc in docs:
                post_data = doc.to_dict()
                post_data['post_id'] = doc.id
                posts.append(post_data)
            
            # Sort posts locally by created_at in descending order
            if posts:
                # Extract date safely
                def get_sort_date(post):
                    created_at = post.get('created_at', '')
                    if created_at:
                        try:
                            # Handle both string and datetime objects
                            if isinstance(created_at, str):
                                return created_at
                            elif hasattr(created_at, 'isoformat'):
                                return created_at.isoformat()
                        except:
                            pass
                    return ''
                
                posts.sort(key=lambda x: get_sort_date(x), reverse=True)
            
            print(f"✅ Found {len(posts)} posts for user {user_id}")
            return posts
            
        except Exception as e:
            print(f"❌ Error getting user posts: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return empty list instead of crashing
            return []
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a post by ID"""
        try:
            doc_ref = self.db.collection('posts').document(post_id)
            doc_ref.delete()
            print(f"✅ Post deleted: {post_id}")
            return True
        except Exception as e:
            raise Exception(f"Error deleting post: {str(e)}")