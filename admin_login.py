import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Add project to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class AdminApp:
    def __init__(self):
        """Initialize Admin Application"""
        from frontend.admin_window import AdminWindow
        from frontend.login_window import LoginWindow
        from backend.auth import AuthManager
        from backend.database import FirebaseDB
        
        try:
            print("🚀 Starting Admin Application...")
            print("=" * 50)
            
            # Initialize components
            self.db = FirebaseDB()
            self.auth_manager = AuthManager()
            self.auth_manager.db = self.db
            
            # Create QApplication
            if hasattr(Qt, 'AA_EnableHighDpiScaling'):
                QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
                QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Blood Donation System - Admin")
            self.app.setApplicationDisplayName("Blood Donation System - Admin")
            
            # Create and show login window for admin
            self.login_window = LoginWindow(self.auth_manager, 'admin')
            self.login_window.login_success.connect(self.on_login_success)
            self.login_window.setWindowTitle("Admin Login - Blood Donation System")
            self.login_window.showMaximized()
            
            print("✅ Admin application started successfully!")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error initializing admin app: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(None, "Error", 
                               f"Failed to start admin application:\n{str(e)}")
            sys.exit(1)
    
    def on_login_success(self, user_info):
        """Handle successful admin login"""
        try:
            print(f"✅ Admin login successful for: {user_info['user_data'].get('email')}")
            
            # Check if user is actually admin
            if not self.auth_manager.is_admin(user_info['user_data']):
                QMessageBox.critical(self.login_window, "Access Denied", 
                                   "This is not an admin account!")
                return
            
            # Show admin dashboard
            from frontend.admin_window import AdminWindow
            self.admin_window = AdminWindow(user_info, self.db)
            self.admin_window.logout_signal.connect(self.on_logout)
            self.admin_window.showMaximized()
            
            # Close login window
            self.login_window.close()
            
            print("✅ Admin dashboard loaded")
            
        except Exception as e:
            print(f"❌ Error loading admin dashboard: {e}")
            QMessageBox.critical(self.login_window, "Error", 
                               f"Failed to load admin dashboard:\n{str(e)}")
    
    def on_logout(self):
        """Handle logout"""
        print("🔐 Admin logging out...")
        
        # Reset auth manager
        if self.auth_manager:
            self.auth_manager.logout()
        
        # Close admin window and show login again
        self.admin_window.close()
        
        # Re-create login window
        from frontend.login_window import LoginWindow
        self.login_window = LoginWindow(self.auth_manager, 'admin')
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.setWindowTitle("Admin Login - Blood Donation System")
        self.login_window.showMaximized()
        
        print("✅ Admin logout successful")
    
    def run(self):
        """Run the admin application"""
        return self.app.exec_()

def main():
    """Main entry point for admin application"""
    admin_app = AdminApp()
    return_code = admin_app.run()
    print(f"\n📱 Admin application exited with code: {return_code}")
    return return_code

if __name__ == "__main__":
    sys.exit(main())