import sys
import os
import warnings
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user_info = None
        self.auth_manager = None
        self.db = None
        
        # Set window properties
        self.setWindowTitle("Blood Donation System")
        self.setGeometry(100, 50, 1400, 800)
        
        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                font-weight: 500;
                border-radius: 5px;
                padding: 10px;
                min-height: 40px;
            }
            QLineEdit, QTextEdit, QComboBox {
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #ddd;
                font-size: 14px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Create central stacked widget
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # Initialize application
        self.init_app()
    
    def init_app(self):
        """Initialize the application components"""
        try:
            print("Initializing application components...")
            
            # Import modules here to avoid circular imports
            from backend.auth import AuthManager
            from backend.database import FirebaseDB
            
            # Initialize Firebase only once
            print("Connecting to database...")
            self.db = FirebaseDB()
            
            # Create auth manager with existing db instance
            print("Setting up authentication...")
            self.auth_manager = AuthManager()
            self.auth_manager.db = self.db  # Use the same db instance
            
            # Create and add initial screen (Role Selection)
            from frontend.role_selection_window import RoleSelectionWindow
            self.role_window = RoleSelectionWindow()
            self.role_window.role_selected.connect(self.show_login_for_role)
            self.role_window.show_signup.connect(self.show_signup)
            
            self.central_widget.addWidget(self.role_window)
            print("✅ Application initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing app: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", 
                               f"Failed to initialize application:\n{str(e)}\n\n"
                               "Please check your Firebase configuration.")
    
    def show_login_for_role(self, role):
        """Show login window for selected role"""
        try:
            from frontend.login_window import LoginWindow
            
            self.login_window = LoginWindow(self.auth_manager, role)
            self.login_window.login_success.connect(self.on_login_success)
            self.login_window.back_to_role.connect(self.show_role_selection)
            
            self.central_widget.addWidget(self.login_window)
            self.central_widget.setCurrentWidget(self.login_window)
            
        except Exception as e:
            print(f"❌ Error showing login: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load login screen:\n{str(e)}")
    
    def show_signup(self):
        """Show signup window"""
        try:
            from frontend.signup_window import SignupWindow
            
            self.signup_window = SignupWindow(self.auth_manager)
            self.signup_window.signup_success.connect(self.on_signup_success)
            self.signup_window.back_to_role.connect(self.show_role_selection)
            
            self.central_widget.addWidget(self.signup_window)
            self.central_widget.setCurrentWidget(self.signup_window)
            
        except Exception as e:
            print(f"❌ Error showing signup: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load signup screen:\n{str(e)}")
    
    def on_login_success(self, user_info):
        """Handle successful login - No popup, directly go to dashboard"""
        try:
            print(f"✅ Login successful for: {user_info['user_data'].get('email')}")
            self.current_user_info = user_info
            
            # Check if admin or user
            is_admin = self.auth_manager.is_admin(user_info['user_data'])
            print(f"   User type: {'Admin' if is_admin else 'Regular User'}")
            
            if is_admin:
                print("   Loading admin dashboard...")
                self.show_admin_dashboard()
            else:
                print("   Loading user dashboard...")
                self.show_user_dashboard()
                
        except Exception as e:
            print(f"❌ Error after login: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load dashboard:\n{str(e)}")
    
    def show_admin_dashboard(self):
        """Show admin dashboard"""
        try:
            from frontend.admin_window import AdminWindow
            
            self.admin_window = AdminWindow(self.current_user_info, self.db)
            self.admin_window.logout_signal.connect(self.on_logout)
            
            self.central_widget.addWidget(self.admin_window)
            self.central_widget.setCurrentWidget(self.admin_window)
            
            print("✅ Admin dashboard loaded")
            
        except Exception as e:
            print(f"❌ Error showing admin dashboard: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load admin dashboard:\n{str(e)}")
    
    def show_user_dashboard(self):
        """Show user dashboard"""
        try:
            from frontend.user_window import UserWindow
            
            self.user_window = UserWindow(self.current_user_info, self.db)
            self.user_window.logout_signal.connect(self.on_logout)
            
            self.central_widget.addWidget(self.user_window)
            self.central_widget.setCurrentWidget(self.user_window)
            
            print("✅ User dashboard loaded")
            
        except Exception as e:
            print(f"❌ Error showing user dashboard: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load user dashboard:\n{str(e)}")
    
    def on_signup_success(self):
        """Handle successful signup"""
        print("✅ Signup successful")
        # Go back to role selection
        self.show_role_selection()
    
    def show_role_selection(self):
        """Show role selection screen"""
        self.central_widget.setCurrentWidget(self.role_window)
    
    def on_logout(self):
        """Handle logout"""
        print("🔐 Logging out...")
        
        # Clear user info
        self.current_user_info = None
        
        # Reset auth manager
        if self.auth_manager:
            self.auth_manager.logout()
        
        # Go back to role selection
        self.show_role_selection()
        print("✅ Logout successful")

def main():
    """Main application entry point"""
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Blood Donation System")
    app.setApplicationDisplayName("Blood Donation System")
    
    # Add project to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        print("🚀 Starting Blood Donation System...")
        print("=" * 50)
        
        # Create and show main window
        window = MainApp()
        window.showMaximized()  # Start maximized
        
        print("✅ Application started successfully!")
        print("=" * 50)
        
        # Run application
        return_code = app.exec_()
        print(f"\n📱 Application exited with code: {return_code}")
        return return_code
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "Fatal Error", 
                           f"Application failed to start:\n{str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())