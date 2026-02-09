from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)
    back_to_role = pyqtSignal()
    signup_requested = pyqtSignal()  # Add this line

    def __init__(self, auth_manager, role):
        super().__init__()
        self.auth_manager = auth_manager
        self.role = role  # 'user' or 'admin'
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # REMOVE THE BACK BUTTON SECTION COMPLETELY
        # We don't need back button in standalone apps
        
        # Title
        role_text = "Admin" if self.role == 'admin' else "User"
        title = QLabel(f"{role_text} Login")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-top: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel(f"Welcome back! Please login to continue as {role_text.lower()}.")
        subtitle.setFont(QFont('Arial', 12))
        subtitle.setStyleSheet("color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Login Form Frame
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #e0e0e0;
            }
        """)
        form_frame.setMaximumWidth(500)
        form_frame.setMinimumWidth(400)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(40, 40, 40, 40)
        
        # Email Input
        email_layout = QVBoxLayout()
        email_label = QLabel("Email Address:")
        email_label.setFont(QFont('Arial', 11, QFont.Bold))
        email_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        email_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setFont(QFont('Arial', 12))
        self.email_input.setMinimumHeight(45)
        email_layout.addWidget(self.email_input)
        form_layout.addLayout(email_layout)
        
        # Password Input
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFont(QFont('Arial', 11, QFont.Bold))
        password_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        password_layout.addWidget(password_label)
        
        password_input_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFont(QFont('Arial', 12))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        password_input_layout.addWidget(self.password_input)
        
        # Show/Hide Password Button
        self.show_password_btn = QPushButton()
        self.show_password_btn.setIcon(QIcon("👁️"))  # You can use an actual eye icon image
        self.show_password_btn.setFixedSize(45, 45)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_input_layout.addWidget(self.show_password_btn)
        
        password_layout.addLayout(password_input_layout)
        form_layout.addLayout(password_layout)
        
        # Error Label (initially hidden)
        self.error_label = QLabel("")
        self.error_label.setFont(QFont('Arial', 10))
        self.error_label.setStyleSheet("color: #e74c3c; padding: 5px; background-color: #ffeaea; border-radius: 4px;")
        self.error_label.setVisible(False)
        form_layout.addWidget(self.error_label)
        
        # Remember Me Checkbox
        remember_layout = QHBoxLayout()
        self.remember_check = QCheckBox("Remember me")
        self.remember_check.setFont(QFont('Arial', 10))
        self.remember_check.setStyleSheet("color: #7f8c8d;")
        remember_layout.addWidget(self.remember_check)
        remember_layout.addStretch()
        form_layout.addLayout(remember_layout)
        
                # ... previous code ...

        # Login Button
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont('Arial', 14, QFont.Bold))
        login_btn.setMinimumHeight(50)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #e0a19a;
            }
        """)
        login_btn.clicked.connect(self.login)
        form_layout.addWidget(login_btn)
        
        layout.addWidget(form_frame, 0, Qt.AlignCenter)
        
                # CENTERED Additional Options
        options_container = QWidget()
        options_container.setMaximumWidth(500)
        options_container.setMinimumWidth(400)
        
        options_layout = QHBoxLayout(options_container)
        options_layout.setSpacing(10)  # Reduced spacing since we're adding text
        options_layout.setContentsMargins(0, 20, 0, 0)  # Add top margin
        
        # Forgot Password Button
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setFont(QFont('Arial', 11))
        forgot_btn.setStyleSheet("""
            QPushButton {
                color: #3498db;
                background: transparent;
                border: none;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        forgot_btn.clicked.connect(self.forgot_password)
        options_layout.addWidget(forgot_btn)
        
        # Only show signup option for user login, not admin
        if self.role == 'user':
            # Add "Don't have an account?" text
            no_account_label = QLabel("Don't have an account?")
            no_account_label.setFont(QFont('Arial', 11))
            no_account_label.setStyleSheet("color: #7f8c8d;")
            options_layout.addWidget(no_account_label)
            
            # Sign Up Button
            signup_btn = QPushButton("Sign Up")
            signup_btn.setFont(QFont('Arial', 11, QFont.Bold))
            signup_btn.setStyleSheet("""
                QPushButton {
                    color: #27ae60;
                    background: transparent;
                    border: none;
                    text-decoration: underline;
                    padding: 5px;
                }
                QPushButton:hover {
                    color: #219653;
                }
            """)
            signup_btn.clicked.connect(self.show_signup_dialog)
            options_layout.addWidget(signup_btn)
        
        # Center the buttons by adding equal stretches on both sides
        options_layout.insertStretch(0, 1)
        options_layout.addStretch(1)
        
        layout.addWidget(options_container, 0, Qt.AlignCenter)
        
        # Footer
        role_text_footer = "Admin" if self.role == 'admin' else "User"
        footer = QLabel(f"Logging in as {role_text_footer} | Need help? Contact bloodbanka485@gmail.com")
        footer.setFont(QFont('Arial', 10))
        footer.setStyleSheet("color: #95a5a6; margin-top: 30px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("👁️")
    
    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # Clear previous error
        self.error_label.setVisible(False)
        self.error_label.setText("")
        
        # Validation
        if not email:
            self.show_error("Please enter your email address.")
            return
        
        if not password:
            self.show_error("Please enter your password.")
            return
        
        try:
            user_info = self.auth_manager.login(email, password)
            
            # Check if admin login matches selection
            is_admin = self.auth_manager.is_admin(user_info['user_data'])
            
            if is_admin and self.role != 'admin':
                self.show_error("This is an admin account. Please use the admin application.")
                return
            elif not is_admin and self.role == 'admin':
                self.show_error("This is not an admin account. Please use the user application.")
                return
            
            # Success - emit signal without popup
            print(f"✅ Login successful for {email}")
            self.login_success.emit(user_info)
            
        except Exception as e:
            self.show_error(str(e))
    
    def show_error(self, message):
        """Show error message below login button"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
    
    def forgot_password(self):
        email, ok = QInputDialog.getText(self, "Reset Password", 
                                        "Enter your email address:")
        if ok and email:
            try:
                self.auth_manager.reset_password(email)
                # Show success message without popup
                self.show_error("Password reset email sent! Check your inbox.")
            except Exception as e:
                self.show_error(str(e))
                
    def show_signup_dialog(self):
        """Show signup dialog (only for user role)"""
        if self.role == 'user':
            self.signup_requested.emit()
    
    def on_signup_success(self):
        """Handle successful signup"""
        # Show success message in the login window
        self.show_error("Account created successfully! Please login with your credentials.")