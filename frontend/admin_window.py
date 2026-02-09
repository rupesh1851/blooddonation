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
        self.show_all_members()  # Show all members by default when window opens
    
    def initUI(self):
        self.setWindowTitle('Blood Donation System - Admin Panel')
        self.setGeometry(100, 50, 1400, 800)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(370)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
            QLabel {
                color: white;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(20)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        
        # Welcome Label
        welcome_label = QLabel(f"🛡️ Welcome, Admin")
        welcome_label.setFont(QFont('Arial', 16, QFont.Bold))
        welcome_label.setStyleSheet("color: white; padding-bottom: 10px; border-bottom: 2px solid #34495e;")
        sidebar_layout.addWidget(welcome_label)
        
        # Admin Info
        info_text = f"""
        <p><b>Name:</b> {self.user_info['user_data']['name']}</p>
        <p><b>Email:</b> {self.user_info['user_data']['email']}</p>
        <p><b>Role:</b> Administrator</p>
        """
        info_label = QLabel(info_text)
        info_label.setFont(QFont('Arial', 11))
        info_label.setStyleSheet("color: #ecf0f1; background-color: #34495e; padding: 15px; border-radius: 8px;")
        info_label.setTextFormat(Qt.RichText)
        sidebar_layout.addWidget(info_label)
        
        sidebar_layout.addSpacing(20)
        
        # Navigation Buttons
        nav_buttons = [
            ("👥 All Members", self.show_all_members),
            ("🩸 Blood Groups", self.show_blood_groups),
            ("📊 Statistics", self.show_statistics),
            ("📝 Posts", self.show_posts),
            ("🚪 Logout", self.logout)
        ]
        
        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setFixedHeight(50)
            btn.setFont(QFont('Arial', 12))
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 20px;
                    background-color: #34495e;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #4a6986;
                }
                QPushButton:pressed {
                    background-color: #1a252f;
                }
            """)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        
        # Right Content Area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f8f9fa;")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(20)
        
        # Content Header
        self.content_header = QLabel("👥 All Members")
        self.content_header.setFont(QFont('Arial', 20, QFont.Bold))
        self.content_header.setStyleSheet("color: #2c3e50;")
        self.content_layout.addWidget(self.content_header)
        
        # Content Table/Widget Container
        self.content_widget = QWidget()
        self.content_layout.addWidget(self.content_widget)
        
        main_layout.addWidget(self.content_area, 1)
    
    def clear_content(self):
        """Remove existing content widget"""
        if self.content_widget:
            # Get the layout of content_widget
            layout = self.content_widget.layout()
            if layout:
                # Clear all widgets from the layout
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
                        widget.deleteLater()
                # Don't try to set the layout to another widget
                # Just let it be garbage collected
            
            # Remove the widget from its parent
            if self.content_widget.parent():
                self.content_widget.parent().layout().removeWidget(self.content_widget)
            
            self.content_widget.deleteLater()
            self.content_widget = None
        
        # Create new content widget
        self.content_widget = QWidget()
        self.content_layout.insertWidget(1, self.content_widget)

    def show_all_members(self):
        """Show all registered users with search functionality"""
        self.clear_content()
        self.content_header.setText("👥 All Members")
        
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search members by name, email, blood group, or location...")
        self.search_input.setFont(QFont('Arial', 12))
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self.filter_members_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.members_table = QTableWidget()  # Make it an instance variable
        self.members_table.setColumnCount(7)
        self.members_table.setHorizontalHeaderLabels([
            "👤 Name", "📧 Email", "📞 Contact", "🩸 Blood Group", 
            "📍 Location", "📅 Last Donation", "📅 Next Available"
        ])  # Changed from "Status" to "Next Available"
        
        # Style the table
        self.members_table.setFont(QFont('Arial', 11))
        self.members_table.setAlternatingRowColors(True)
        self.members_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.members_table.horizontalHeader().setStretchLastSection(True)
        self.members_table.verticalHeader().setVisible(False)
        
        # Store original data
        self.all_users = self.db.get_all_users()
        
        # Populate table with all users initially
        self.populate_members_table(self.all_users)
        
        layout.addWidget(self.members_table)
        
        # Summary
        self.summary_label = QLabel()  # Make it an instance variable
        self.summary_label.setFont(QFont('Arial', 11))
        self.summary_label.setStyleSheet("color: #7f8c8d; padding: 10px;")
        self.update_summary_label(self.all_users)
        layout.addWidget(self.summary_label)

    def populate_members_table(self, users):
        """Populate table with given users list"""
        self.members_table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            # Set row background based on user type
            if user.get('user_type') == 'admin':
                for col in range(7):
                    item = QTableWidgetItem()
                    item.setBackground(QColor(255, 243, 205))  # Light yellow for admin
                    self.members_table.setItem(i, col, item)
            
            # CORRECT COLUMN ORDER:
            self.members_table.setItem(i, 0, QTableWidgetItem(user.get('name', '')))
            self.members_table.setItem(i, 1, QTableWidgetItem(user.get('email', '')))
            self.members_table.setItem(i, 2, QTableWidgetItem(user.get('contact_number', '')))
            self.members_table.setItem(i, 3, QTableWidgetItem(user.get('blood_group', '')))
            self.members_table.setItem(i, 4, QTableWidgetItem(user.get('location', '')))
            self.members_table.setItem(i, 5, QTableWidgetItem(user.get('last_donation', 'Never')))
            
            # Next Available date with color coding - CORRECT COLUMN (6)
            if user.get('user_type') == 'admin':
                status_item = QTableWidgetItem("Admin")
                status_item.setForeground(QColor(230, 126, 34))  # Orange for admin
            else:
                next_available = user.get('next_available', 'Not set')
                if next_available and next_available != 'Not set' and next_available != 'null':
                    # Format the date nicely
                    try:
                        # If it's in YYYY-MM-DD format, convert to DD/MM/YYYY
                        if '-' in next_available:
                            parts = next_available.split('-')
                            if len(parts) == 3:
                                next_available = f"{parts[2]}/{parts[1]}/{parts[0]}"
                        
                        # Check if date has passed (available for donation)
                        from datetime import datetime
                        today = datetime.now().date()
                        next_date = datetime.strptime(next_available.replace('/', '-'), '%d-%m-%Y').date()
                        
                        if next_date <= today:
                            status_item = QTableWidgetItem("Available Now")
                            status_item.setForeground(QColor(39, 174, 96))  # Green for available
                            status_item.setBackground(QColor(235, 255, 238))
                        else:
                            status_item = QTableWidgetItem(f"From {next_available}")
                            status_item.setForeground(QColor(52, 152, 219))  # Blue for future date
                    except:
                        # If date parsing fails, show as is
                        status_item = QTableWidgetItem(next_available)
                        status_item.setForeground(QColor(149, 165, 166))  # Gray for unparsed
                else:
                    status_item = QTableWidgetItem("Not set")
                    status_item.setForeground(QColor(149, 165, 166))  # Gray for not set
            
            self.members_table.setItem(i, 6, status_item)
        
        self.members_table.resizeColumnsToContents()
        self.resize_table_headers()

    def update_summary_label(self, users):
        """Update summary label with current user count"""
        admin_count = len([u for u in users if u.get('user_type') == 'admin'])
        user_count = len(users) - admin_count
        self.summary_label.setText(f"📊 Total Members: {len(users)} (Admins: {admin_count}, Users: {user_count})")

    def filter_members_table(self):
        """Filter table based on search input"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            # Show all users if search is empty
            filtered_users = self.all_users
        else:
            # Filter users based on search criteria
            filtered_users = []
            for user in self.all_users:
                # Check if search text exists in name, email, blood group, or location
                name_match = search_text in user.get('name', '').lower()
                email_match = search_text in user.get('email', '').lower()
                blood_group_match = search_text in user.get('blood_group', '').lower()
                location_match = search_text in user.get('location', '').lower()
                
                # Also search in next available date
                next_available = user.get('next_available', '')
                next_available_match = search_text in str(next_available).lower()
                
                if name_match or email_match or blood_group_match or location_match or next_available_match:
                    filtered_users.append(user)
        
        # Update table with filtered results
        self.populate_members_table(filtered_users)
        self.update_summary_label(filtered_users)

    # Also update the show_blood_groups method to fix the summary text:
    def show_blood_groups(self):
        """Show blood group distribution"""
        self.clear_content()
        self.content_header.setText("🩸 Blood Group Distribution")
        
        layout = QVBoxLayout(self.content_widget)
        layout.setSpacing(15)
        
        # Get all blood groups
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["🩸 Blood Group", "👥 Count", "📊 Percentage", "👤 Members"])
        
        table.setFont(QFont('Arial', 11))
        table.setAlternatingRowColors(True)
        
        total_users = len(self.db.get_all_users())
        table.setRowCount(len(blood_groups))
        
        # Find most common blood group
        blood_group_counts = {}
        for bg in blood_groups:
            users = self.db.get_users_by_blood_group(bg)
            blood_group_counts[bg] = len(users)
        
        most_common_bg = max(blood_group_counts.items(), key=lambda x: x[1]) if blood_group_counts else ("None", 0)
        
        for i, bg in enumerate(blood_groups):
            users = self.db.get_users_by_blood_group(bg)
            count = len(users)
            percentage = (count / total_users * 100) if total_users > 0 else 0
            
            # Blood group with color
            bg_item = QTableWidgetItem(bg)
            bg_item.setForeground(QColor(231, 76, 60))  # Red for blood group
            table.setItem(i, 0, bg_item)
            
            # Count
            table.setItem(i, 1, QTableWidgetItem(str(count)))
            
            # Percentage with progress bar effect
            percent_item = QTableWidgetItem(f"{percentage:.1f}%")
            table.setItem(i, 2, percent_item)
            
            # Member names
            member_names = ", ".join([user['name'] for user in users[:3]])
            if count > 3:
                member_names += f" (+{count-3} more)"
            elif count == 0:
                member_names = "No members"
            table.setItem(i, 3, QTableWidgetItem(member_names))
        
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        layout.addWidget(table)
        
        # Updated summary with most common blood group
        summary = QLabel(f"📊 Total Members: {total_users} | Most common: {most_common_bg[0]} ({most_common_bg[1]} members)")
        summary.setFont(QFont('Arial', 11))
        summary.setStyleSheet("color: #7f8c8d; padding: 10px;")
        layout.addWidget(summary)

    def show_statistics(self):
        """Show system statistics"""
        self.clear_content()
        self.content_header.setText("📊 System Statistics")
        
        layout = QVBoxLayout(self.content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Get statistics
        users = self.db.get_all_users()
        posts = self.db.get_all_posts()
        
        # Get today's date
        from datetime import datetime, date
        today = date.today().isoformat()  # Returns '2026-02-04'
        
        # Count posts created today
        posts_today = 0
        for post in posts:
            created_at = post.get('created_at', '')
            if created_at:
                # Extract date part from timestamp (could be '2026-02-04T12:34:56.789Z' or '2026-02-04')
                if 'T' in created_at:
                    post_date = created_at.split('T')[0]  # Get '2026-02-04' from '2026-02-04T12:34:56.789Z'
                else:
                    post_date = created_at[:10]  # Get first 10 characters
                
                if post_date == today:
                    posts_today += 1
        
        # Stats Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        stats_data = [
            ("👥 Total Users", len(users), "#3498db"),
            ("📝 Total Posts", len(posts), "#9b59b6"),
            ("🟢 Open Requests", len([p for p in posts if p.get('status') == 'open']), "#2ecc71"),
            ("✅ Fulfilled Requests", len([p for p in posts if p.get('status') == 'fulfilled']), "#27ae60"),
            ("📅 Posts Today", posts_today, "#f39c12"),  # Fixed: Now shows actual posts from today
            ("🩸 Unique Blood Groups", len(set([u.get('blood_group', '') for u in users if u.get('blood_group')])), "#e74c3c")
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            stat_widget = QFrame()
            stat_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border-radius: 10px;
                    border-left: 5px solid {color};
                    padding: 20px;
                    min-height: 120px;
                }}
            """)
            
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setAlignment(Qt.AlignTop)
            
            title_label = QLabel(title)
            title_label.setFont(QFont('Arial', 12))
            title_label.setStyleSheet(f"color: {color}; font-weight: bold; margin-bottom: 10px;")
            stat_layout.addWidget(title_label)
            
            value_label = QLabel(str(value))
            value_label.setFont(QFont('Arial', 28, QFont.Bold))
            value_label.setStyleSheet("color: #2c3e50;")
            value_label.setAlignment(Qt.AlignCenter)
            stat_layout.addWidget(value_label)
            
            row = i // 3
            col = i % 3
            grid_layout.addWidget(stat_widget, row, col)
        
        layout.addLayout(grid_layout)
        layout.addStretch()

    def show_posts(self):                                              
        """Show all donation posts"""
        self.clear_content()
        self.content_header.setText("📝 Donation Posts")
        
        layout = QVBoxLayout(self.content_widget)
        layout.setSpacing(15)#
        
        # Filter buttons
        filter_layout = QHBoxLayout()
        
        # Create filter buttons and store reference to current filter
        self.current_post_filter = 'all'  # Track current filter
        
        filter_buttons = [
            ("All Posts", 'all'),
            ("Open", 'open'),
            ("Fulfilled", 'fulfilled')
        ]
        
        for text, filter_type in filter_buttons:
            btn = QPushButton(text)
            btn.setFont(QFont('Arial', 11))
            btn.setCheckable(True)  # Make button checkable
            btn.setChecked(filter_type == 'all')  # Initially check "All Posts"
            
            # Store filter type as property
            btn.filter_type = filter_type
            
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 8px 15px;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
                QPushButton:pressed {
                    background-color: #bfc9ca;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    color: white;
                    border: 1px solid #2980b9;
                }
            """)
            btn.clicked.connect(lambda checked, ft=filter_type: self.filter_posts(ft))
            filter_layout.addWidget(btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Create table as instance variable so we can access it in filter_posts
        self.posts_table = QTableWidget()
        self.posts_table.setColumnCount(7)
        self.posts_table.setHorizontalHeaderLabels([
            "👤 Posted By", "🩸 Blood Needed", "📍 Location", 
            "📞 Contact", "⚠️ Urgency", "🟢 Status", "📅 Date"#, "🆔 Post ID"
        ])
        
        self.posts_table.setFont(QFont('Arial', 11))
        self.posts_table.setAlternatingRowColors(True)
        
        # Store all posts for filtering
        self.all_posts = self.db.get_all_posts()
        
        # Initially show all posts
        self.display_posts(self.all_posts)
        
        self.posts_table.horizontalHeader().setStretchLastSection(True)
        self.posts_table.resizeColumnsToContents()
        layout.addWidget(self.posts_table)
        
        # Summary label as instance variable for updating
        self.posts_summary_label = QLabel()
        self.posts_summary_label.setFont(QFont('Arial', 11))
        self.posts_summary_label.setStyleSheet("color: #7f8c8d; padding: 10px;")
        self.update_posts_summary(self.all_posts)
        layout.addWidget(self.posts_summary_label)

    def display_posts(self, posts):
        """Display posts in the table"""
        self.posts_table.setRowCount(len(posts))
        
        for i, post in enumerate(posts):
            self.posts_table.setItem(i, 0, QTableWidgetItem(post.get('user_name', '')))
            self.posts_table.setItem(i, 1, QTableWidgetItem(post.get('blood_group_needed', '')))
            self.posts_table.setItem(i, 2, QTableWidgetItem(post.get('location', '')))
            self.posts_table.setItem(i, 3, QTableWidgetItem(post.get('contact_number', '')))
            
            # Urgency with color
            urgency = post.get('urgency', 'medium')
            urgency_item = QTableWidgetItem(urgency.capitalize())
            if urgency == 'high':
                urgency_item.setForeground(QColor(231, 76, 60))
                urgency_item.setBackground(QColor(255, 235, 238))
            elif urgency == 'medium':
                urgency_item.setForeground(QColor(241, 196, 15))
                urgency_item.setBackground(QColor(255, 249, 235))
            else:
                urgency_item.setForeground(QColor(46, 204, 113))
                urgency_item.setBackground(QColor(235, 255, 238))
            self.posts_table.setItem(i, 4, urgency_item)
            
            # Status with color
            status = post.get('status', 'open')
            status_item = QTableWidgetItem(status.capitalize())
            if status == 'open':
                status_item.setForeground(QColor(39, 174, 96))
            elif status == 'fulfilled':
                status_item.setForeground(QColor(52, 152, 219))
            else:
                status_item.setForeground(QColor(149, 165, 166))
            self.posts_table.setItem(i, 5, status_item)
            
            # Date
            date = post.get('created_at', '')
            if date:
                date = date[:10]  # Get only date part
            self.posts_table.setItem(i, 6, QTableWidgetItem(date))
            
            # Post ID (shortened)
            post_id = post.get('id', '')
            if len(post_id) > 8:
                post_id = post_id[:8] + "..."
            self.posts_table.setItem(i, 7, QTableWidgetItem(post_id))
        
        self.posts_table.resizeColumnsToContents()

    def update_posts_summary(self, posts):
        """Update posts summary label"""
        open_count = len([p for p in posts if p.get('status') == 'open'])
        fulfilled_count = len([p for p in posts if p.get('status') == 'fulfilled'])
        other_count = len(posts) - open_count - fulfilled_count
        
        summary_text = f"📊 Total: {len(posts)} posts | 🟢 Open: {open_count} | ✅ Fulfilled: {fulfilled_count}"
        if other_count > 0:
            summary_text += f" | ⚪ Other: {other_count}"
        
        self.posts_summary_label.setText(summary_text)

    def filter_posts(self, status):
        """Filter posts by status"""
        self.current_post_filter = status
        
        if status == 'all':
            filtered_posts = self.all_posts
        elif status == 'open':
            filtered_posts = [post for post in self.all_posts if post.get('status') == 'open']
        elif status == 'fulfilled':
            filtered_posts = [post for post in self.all_posts if post.get('status') == 'fulfilled']
        else:
            filtered_posts = self.all_posts
        
        # Update the table with filtered posts
        self.display_posts(filtered_posts)
        
        # Update the summary
        self.update_posts_summary(filtered_posts)
        
        # Update button states (uncheck all, check the clicked one)
        for btn in self.content_widget.findChildren(QPushButton):
            if hasattr(btn, 'filter_type'):
                btn.setChecked(btn.filter_type == status)

    def resize_table_headers(self):
        """Resize table headers to fit content"""
        header = self.members_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Name
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Contact
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Blood Group
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Location
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Last Donation
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Next Available

    def logout(self):
        """Logout method - emits signal"""
        print("AdminWindow: Logout clicked")
        self.logout_signal.emit()
        self.close()