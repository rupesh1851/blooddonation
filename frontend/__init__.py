from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class AdminWindow(QMainWindow):
    logout_signal = pyqtSignal()
    
    def __init__(self, user_info, db):
        super().__init__()
        self.user_info = user_info
        self.db = db
        self.initUI()
        # FIXED: Don't call load_all_users() here, it's called by show_all_members()
        # which is the default view
    
    def initUI(self):
        self.setWindowTitle('Blood Donation System - Admin Panel')
        self.setGeometry(100, 50, 1200, 700)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Welcome Label
        welcome_label = QLabel(f"Welcome, {self.user_info['user_data']['name']}")
        welcome_label.setFont(QFont('Arial', 12, QFont.Bold))
        sidebar_layout.addWidget(welcome_label)
        
        sidebar_layout.addSpacing(20)
        
        # Navigation Buttons
        nav_buttons = [
            ("All Members", self.show_all_members),
            ("Blood Groups", self.show_blood_groups),
            ("Statistics", self.show_statistics),
            ("Posts", self.show_posts),
            ("Logout", self.logout)
        ]
        
        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 20px;
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
            """)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        
        # Right Content Area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        
        # Content Header
        self.content_header = QLabel("All Members")
        self.content_header.setFont(QFont('Arial', 14, QFont.Bold))
        self.content_layout.addWidget(self.content_header)
        
        # Content Table/Widget
        self.content_widget = QWidget()
        self.content_layout.addWidget(self.content_widget)
        
        main_layout.addWidget(self.content_area, 1)
        
        # Show all members by default
        self.show_all_members()
    
    def clear_content(self):
        """Remove existing content widget"""
        if self.content_widget:
            # Get the layout of content_widget
            layout = self.content_widget.layout()
            if layout:
                # Remove all widgets from layout
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            else:
                # If no layout, just delete the widget
                self.content_widget.deleteLater()
        
        # Create new content widget
        self.content_widget = QWidget()
        self.content_layout.insertWidget(1, self.content_widget)
    
    def show_all_members(self):
        """Show all registered users"""
        self.clear_content()
        self.content_header.setText("All Members")
        
        layout = QVBoxLayout(self.content_widget)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Name", "Email", "Contact", "Blood Group", 
            "Location", "Last Donation", "Status"
        ])
        
        # Get users from database
        users = self.db.get_all_users()
        table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            table.setItem(i, 0, QTableWidgetItem(user.get('name', '')))
            table.setItem(i, 1, QTableWidgetItem(user.get('email', '')))
            table.setItem(i, 2, QTableWidgetItem(user.get('contact_number', '')))
            table.setItem(i, 3, QTableWidgetItem(user.get('blood_group', '')))
            table.setItem(i, 4, QTableWidgetItem(user.get('location', '')))
            table.setItem(i, 5, QTableWidgetItem(user.get('last_donation', 'Never')))
            status = "Active" if user.get('user_type') != 'admin' else "Admin"
            table.setItem(i, 6, QTableWidgetItem(status))
        
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)
    
    def show_blood_groups(self):
        """Show blood group distribution"""
        self.clear_content()
        self.content_header.setText("Blood Group Distribution")
        
        layout = QVBoxLayout(self.content_widget)
        
        # Get all blood groups
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Blood Group", "Count", "Members"])
        
        table.setRowCount(len(blood_groups))
        
        for i, bg in enumerate(blood_groups):
            users = self.db.get_users_by_blood_group(bg)
            count = len(users)
            
            table.setItem(i, 0, QTableWidgetItem(bg))
            table.setItem(i, 1, QTableWidgetItem(str(count)))
            
            member_names = ", ".join([user['name'] for user in users[:3]])
            if count > 3:
                member_names += f"... and {count-3} more"
            table.setItem(i, 2, QTableWidgetItem(member_names))
        
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)
    
    def show_statistics(self):
        """Show system statistics"""
        self.clear_content()
        self.content_header.setText("Statistics")
        
        layout = QVBoxLayout(self.content_widget)
        
        # Get statistics
        users = self.db.get_all_users()
        posts = self.db.get_all_posts()
        
        stats_text = f"""
        <h3>System Statistics</h3>
        <p><b>Total Users:</b> {len(users)}</p>
        <p><b>Total Posts:</b> {len(posts)}</p>
        <p><b>Open Requests:</b> {len([p for p in posts if p.get('status') == 'open'])}</p>
        <p><b>Fulfilled Requests:</b> {len([p for p in posts if p.get('status') == 'fulfilled'])}</p>
        """
        
        stats_label = QLabel(stats_text)
        stats_label.setTextFormat(Qt.RichText)
        layout.addWidget(stats_label)
    
    def show_posts(self):
        """Show all donation posts"""
        self.clear_content()
        self.content_header.setText("Donation Posts")
        
        layout = QVBoxLayout(self.content_widget)
        
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Posted By", "Blood Needed", "Location", 
            "Contact", "Urgency", "Status", "Date"
        ])
        
        posts = self.db.get_all_posts()
        table.setRowCount(len(posts))
        
        for i, post in enumerate(posts):
            table.setItem(i, 0, QTableWidgetItem(post.get('user_name', '')))
            table.setItem(i, 1, QTableWidgetItem(post.get('blood_group_needed', '')))
            table.setItem(i, 2, QTableWidgetItem(post.get('location', '')))
            table.setItem(i, 3, QTableWidgetItem(post.get('contact_number', '')))
            
            urgency = post.get('urgency', 'medium')
            urgency_item = QTableWidgetItem(urgency.capitalize())
            if urgency == 'high':
                urgency_item.setForeground(QColor(231, 76, 60))
            elif urgency == 'medium':
                urgency_item.setForeground(QColor(241, 196, 15))
            else:
                urgency_item.setForeground(QColor(46, 204, 113))
            table.setItem(i, 4, urgency_item)
            
            status = post.get('status', 'open')
            status_item = QTableWidgetItem(status.capitalize())
            table.setItem(i, 5, status_item)
            
            date = post.get('created_at', '')[:10]
            table.setItem(i, 6, QTableWidgetItem(date))
        
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)
    
    def logout(self):
        """Logout method - emits signal"""
        print("AdminWindow: Logout clicked")
        self.logout_signal.emit()
        self.close()