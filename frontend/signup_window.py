
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from backend.models import User

class SignupWindow(QDialog):  # Changed from QWidget to QDialog
    signup_success = pyqtSignal()
    
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Create New Account")
        self.setModal(True)  # Make it modal
        
        layout = QVBoxLayout(self)  # Set layout on self
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Create New Account")
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Join our blood donation community and save lives")
        subtitle.setFont(QFont('Arial', 11))
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Form Frame
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 0px;
            }
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Error Label
        self.error_label = QLabel("")
        self.error_label.setFont(QFont('Arial', 10))
        self.error_label.setStyleSheet("color: #e74c3c; padding: 10px; background-color: #ffeaea; border-radius: 4px;")
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        form_layout.addWidget(self.error_label)
        
        # Name Input
        name_layout = QVBoxLayout()
        name_label = QLabel("Full Name:")
        name_label.setFont(QFont('Arial', 10, QFont.Bold))
        name_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        self.name_input.setFont(QFont('Arial', 11))
        self.name_input.setMinimumHeight(38)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        # Email Input
        email_layout = QVBoxLayout()
        email_label = QLabel("Email Address:")
        email_label.setFont(QFont('Arial', 10, QFont.Bold))
        email_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.setFont(QFont('Arial', 11))
        self.email_input.setMinimumHeight(38)
        email_layout.addWidget(self.email_input)
        form_layout.addLayout(email_layout)
        
        # Contact Number
        contact_layout = QVBoxLayout()
        contact_label = QLabel("Contact Number:")
        contact_label.setFont(QFont('Arial', 10, QFont.Bold))
        contact_layout.addWidget(contact_label)
        
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Enter your phone number")
        self.contact_input.setFont(QFont('Arial', 11))
        self.contact_input.setMinimumHeight(38)
        contact_layout.addWidget(self.contact_input)
        form_layout.addLayout(contact_layout)
        
        # Blood Group
        blood_layout = QVBoxLayout()
        blood_label = QLabel("Blood Group:")
        blood_label.setFont(QFont('Arial', 10, QFont.Bold))
        blood_layout.addWidget(blood_label)
        
        self.blood_combo = QComboBox()
        self.blood_combo.addItems(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        self.blood_combo.setFont(QFont('Arial', 11))
        self.blood_combo.setMinimumHeight(38)
        blood_layout.addWidget(self.blood_combo)
        form_layout.addLayout(blood_layout)
        
        # Location
        location_layout = QVBoxLayout()
        location_label = QLabel("Location:")
        location_label.setFont(QFont('Arial', 10, QFont.Bold))
        location_layout.addWidget(location_label)
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter your city/district")
        self.location_input.setFont(QFont('Arial', 11))
        self.location_input.setMinimumHeight(38)
        location_layout.addWidget(self.location_input)
        form_layout.addLayout(location_layout)
        
        # Password
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFont(QFont('Arial', 10, QFont.Bold))
        password_layout.addWidget(password_label)
        
        password_input_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter a strong password (min 6 chars)")
        self.password_input.setFont(QFont('Arial', 11))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(38)
        password_input_layout.addWidget(self.password_input)
        
        self.show_password_btn = QPushButton("👁️")
        self.show_password_btn.setFixedSize(38, 38)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_input_layout.addWidget(self.show_password_btn)
        
        password_layout.addLayout(password_input_layout)
        form_layout.addLayout(password_layout)
        
        # Confirm Password
        confirm_layout = QVBoxLayout()
        confirm_label = QLabel("Confirm Password:")
        confirm_label.setFont(QFont('Arial', 10, QFont.Bold))
        confirm_layout.addWidget(confirm_label)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm your password")
        self.confirm_input.setFont(QFont('Arial', 11))
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setMinimumHeight(38)
        confirm_layout.addWidget(self.confirm_input)
        form_layout.addLayout(confirm_layout)
        
        # Terms Checkbox
        terms_layout = QHBoxLayout()
        self.terms_check = QCheckBox("I agree to the Terms and Conditions")
        self.terms_check.setFont(QFont('Arial', 9))
        self.terms_check.setStyleSheet("color: #7f8c8d;")
        terms_layout.addWidget(self.terms_check)
        terms_layout.addStretch()
        form_layout.addLayout(terms_layout)
        
        layout.addWidget(form_frame)
        
        # Buttons Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Cancel Button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont('Arial', 11))
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        buttons_layout.addStretch()
        
        # Sign Up Button
        signup_btn = QPushButton("Create Account")
        signup_btn.setFont(QFont('Arial', 11, QFont.Bold))
        signup_btn.setFixedHeight(40)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0 30px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        signup_btn.clicked.connect(self.signup)
        buttons_layout.addWidget(signup_btn)
        
        layout.addLayout(buttons_layout)
        
        # Adjust size
        self.setMinimumWidth(500)
        self.setMaximumWidth(700)
    
    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.confirm_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("👁️")
    
    def show_error(self, message):
        """Show error message"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
    
    def clear_error(self):
        """Clear error message"""
        self.error_label.setText("")
        self.error_label.setVisible(False)
    
    def signup(self):
        """Handle signup process"""
        # Clear previous errors
        self.clear_error()
        
        # Get form data
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        contact = self.contact_input.text().strip()
        blood_group = self.blood_combo.currentText()
        location = self.location_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()
        
        # Validation
        if not name:
            self.show_error("Please enter your full name.")
            return
        
        if not email:
            self.show_error("Please enter your email address.")
            return
        
        if not contact:
            self.show_error("Please enter your contact number.")
            return
        
        if not location:
            self.show_error("Please enter your location.")
            return
        
        if not password:
            self.show_error("Please enter a password.")
            return
        
        if password != confirm_password:
            self.show_error("Passwords do not match.")
            return
        
        if len(password) < 6:
            self.show_error("Password must be at least 6 characters long.")
            return
        
        if not self.terms_check.isChecked():
            self.show_error("Please agree to the Terms and Conditions.")
            return
        
        try:
            # Create user object
            user = User(
                name=name,
                email=email,
                contact_number=contact,
                blood_group=blood_group,
                location=location
            )
            
            # Register user
            if self.auth_manager.signup(user, password):
                self.show_error("✅ Account created successfully!")
                # Wait a moment then close
                QTimer.singleShot(1500, self.accept_and_close)
                
        except Exception as e:
            self.show_error(f"❌ {str(e)}")
    
    def accept_and_close(self):
        """Accept and close the dialog"""
        self.signup_success.emit()
        self.accept()
    
    def reject(self):
        """Override reject to close properly"""
        super().reject()