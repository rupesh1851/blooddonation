from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap

class RoleSelectionWindow(QWidget):
    role_selected = pyqtSignal(str)  # 'user' or 'admin'
    show_signup = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("Blood Donation System")
        title.setFont(QFont('Arial', 28, QFont.Bold))
        title.setStyleSheet("color: #e74c3c;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Save Lives, Donate Blood")
        subtitle.setFont(QFont('Arial', 16))
        subtitle.setStyleSheet("color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(50)
        
        # Role Selection Frame
        role_frame = QFrame()
        role_frame.setFrameShape(QFrame.StyledPanel)
        role_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #e0e0e0;
            }
        """)
        role_frame.setMaximumWidth(500)
        role_frame.setMinimumWidth(400)
        
        role_layout = QVBoxLayout(role_frame)
        role_layout.setSpacing(20)
        role_layout.setContentsMargins(40, 40, 40, 40)
        
        # Role Selection Label
        role_label = QLabel("Select Your Role")
        role_label.setFont(QFont('Arial', 18, QFont.Bold))
        role_label.setAlignment(Qt.AlignCenter)
        role_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        role_layout.addWidget(role_label)
        
        # User Button
        user_btn = QPushButton("👤  User Login")
        user_btn.setFont(QFont('Arial', 14))
        user_btn.setFixedHeight(50)
        user_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c5d87;
            }
        """)
        user_btn.clicked.connect(lambda: self.role_selected.emit('user'))
        role_layout.addWidget(user_btn)
        
        # Admin Button
        admin_btn = QPushButton("⚙️  Admin Login")
        admin_btn.setFont(QFont('Arial', 14))
        admin_btn.setFixedHeight(50)
        admin_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #6c3483;
            }
        """)
        admin_btn.clicked.connect(lambda: self.role_selected.emit('admin'))
        role_layout.addWidget(admin_btn)
        
        layout.addWidget(role_frame, 0, Qt.AlignCenter)
        
        layout.addSpacing(30)
        
        # Additional Options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(15)
        
        # Sign Up Button
        signup_btn = QPushButton("Create New Account")
        signup_btn.setFont(QFont('Arial', 12))
        signup_btn.setFixedHeight(40)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                width: 200px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        signup_btn.clicked.connect(self.show_signup.emit)
        options_layout.addWidget(signup_btn, 0, Qt.AlignCenter)
        
        # Forgot Password Button
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setFont(QFont('Arial', 11))
        forgot_btn.setStyleSheet("""
            QPushButton {
                color: #3498db;
                background: transparent;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        forgot_btn.clicked.connect(self.show_forgot_password)
        options_layout.addWidget(forgot_btn, 0, Qt.AlignCenter)
        
        layout.addLayout(options_layout)
        
        # Footer
        footer = QLabel("© 2026 Blood Donation System | Save Lives")
        footer.setFont(QFont('Arial', 10))
        footer.setStyleSheet("color: #95a5a6; margin-top: 30px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def show_forgot_password(self):
        # This will be handled in the login window
        from PyQt5.QtWidgets import QInputDialog
        email, ok = QInputDialog.getText(self, "Reset Password", 
                                        "Enter your email address:")
        if ok and email:
            # You would need to implement password reset here
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Information", 
                                  "Password reset functionality would be implemented here.")