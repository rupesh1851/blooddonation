import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QStackedWidget
from PyQt5.QtCore import Qt

# Add project to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class UserApp:
    def __init__(self):
        """Initialize User Application"""
        from frontend.login_window import LoginWindow
        from frontend.signup_window import SignupWindow
        from backend.auth import AuthManager
        from backend.database import FirebaseDB
        
        try:
            print("🚀 Starting User Application...")
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
            self.app.setApplicationName("Blood Donation System - User")
            self.app.setApplicationDisplayName("Blood Donation System - User")
            
            # Create stacked widget for multiple screens
            self.stacked_widget = QStackedWidget()
            self.stacked_widget.setWindowTitle("Blood Donation System - User")
            
            # Create login window for user directly
            self.login_window = LoginWindow(self.auth_manager, 'user')
            self.login_window.login_success.connect(self.on_login_success)
            self.login_window.signup_requested.connect(self.show_signup)  # Connect signup signal
            
            self.stacked_widget.addWidget(self.login_window)
            self.stacked_widget.showMaximized()
            
            print("✅ User application started successfully!")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error initializing user app: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(None, "Error", 
                               f"Failed to start user application:\n{str(e)}")
            sys.exit(1)
    
    def show_signup(self):
        """Show signup window as a popup dialog"""
        try:
            from frontend.signup_window import SignupWindow
            
            # Create signup window as a dialog
            self.signup_dialog = SignupWindow(self.auth_manager)
            self.signup_dialog.signup_success.connect(self.on_signup_success)
            
            # Set dialog properties for popup behavior
            self.signup_dialog.setWindowTitle("Create New Account")
            self.signup_dialog.setWindowModality(Qt.ApplicationModal)
            self.signup_dialog.resize(700, 800)  # Set size for popup
            self.signup_dialog.show()
            
        except Exception as e:
            print(f"❌ Error showing signup: {e}")
            QMessageBox.critical(self.stacked_widget, "Error", 
                            f"Failed to load signup screen:\n{str(e)}")
    
    def on_login_success(self, user_info):
        """Handle successful user login"""
        try:
            print(f"✅ User login successful for: {user_info['user_data'].get('email')}")
            
            # Check if user is not admin (should be regular user)
            if self.auth_manager.is_admin(user_info['user_data']):
                QMessageBox.critical(self.stacked_widget, "Access Denied", 
                                   "This is an admin account! Please use the admin application.")
                return
            
            # Show user dashboard
            from frontend.user_window import UserWindow
            self.user_window = UserWindow(user_info, self.db)
            self.user_window.logout_signal.connect(self.on_logout)
            
            self.stacked_widget.addWidget(self.user_window)
            self.stacked_widget.setCurrentWidget(self.user_window)
            
            print("✅ User dashboard loaded")
            
        except Exception as e:
            print(f"❌ Error loading user dashboard: {e}")
            QMessageBox.critical(self.stacked_widget, "Error", 
                               f"Failed to load user dashboard:\n{str(e)}")
    
    def on_signup_success(self):
        """Handle successful signup"""
        print("✅ Signup successful")
        
        # Close the signup dialog
        if hasattr(self, 'signup_dialog') and self.signup_dialog:
            self.signup_dialog.close()
        
        # Show success message
        QMessageBox.information(self.login_window, "Signup Successful", 
                            "Account created successfully! Please login with your credentials.")
    
    def show_login(self):
        """Show login window"""
        self.stacked_widget.setCurrentWidget(self.login_window)
        
        # Remove any other windows if they exist
        if hasattr(self, 'signup_window') and self.signup_window:
            self.stacked_widget.removeWidget(self.signup_window)
            self.signup_window = None
    
    def on_logout(self):
        """Handle logout"""
        print("🔐 User logging out...")
        
        # Remove user window from stacked widget
        self.stacked_widget.removeWidget(self.user_window)
        self.user_window = None
        
        # Reset auth manager
        if self.auth_manager:
            self.auth_manager.logout()
        
        # Show login window
        self.stacked_widget.setCurrentWidget(self.login_window)
        print("✅ User logout successful")
    
    def run(self):
        """Run the user application"""
        return self.app.exec_()

def main():
    """Main entry point for user application"""
    user_app = UserApp()
    return_code = user_app.run()
    print(f"\n📱 User application exited with code: {return_code}")
    return return_code

if __name__ == "__main__":
    sys.exit(main())