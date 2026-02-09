from PyQt5.QtCore import pyqtSignal, Qt, QDate
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from backend.models import Post

class UserWindow(QMainWindow):
    logout_signal = pyqtSignal()
    
    def __init__(self, user_info, db):
        super().__init__()
        self.user_info = user_info
        self.db = db
        self.user_id = user_info['user_id']
        self.initUI()
        self.load_posts()
    
    def initUI(self):
        self.setWindowTitle('Blood Donation System - User Panel')
        self.setGeometry(100, 50, 1200, 700)
        
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
        self.sidebar_layout = QVBoxLayout(sidebar)  # Make it instance variable
        self.sidebar_layout.setSpacing(20)
        self.sidebar_layout.setContentsMargins(20, 30, 20, 30)
        
        # Welcome Label
        welcome_label = QLabel(f"{self.user_info['user_data']['name']}")
        welcome_label.setFont(QFont('Arial', 16, QFont.Bold))
        welcome_label.setStyleSheet("color: white; padding-bottom: 10px; border-bottom: 2px solid #34495e;")
        self.sidebar_layout.addWidget(welcome_label)
        
        # User Info Box
        self.info_box = QFrame()  # Make it instance variable
        self.info_box.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #ecf0f1;
            }
        """)
        self.info_layout = QVBoxLayout(self.info_box)  # Make it instance variable
        
        # Create info labels as instance variables
        self.blood_label = QLabel(f"🩸 Blood Group: {self.user_info['user_data']['blood_group']}")
        self.blood_label.setFont(QFont('Arial', 12))
        self.info_layout.addWidget(self.blood_label)
        
        self.location_label = QLabel(f"📍 Location: {self.user_info['user_data']['location']}")
        self.location_label.setFont(QFont('Arial', 12))
        self.info_layout.addWidget(self.location_label)
        
        last_donation = self.user_info['user_data'].get('last_donation', 'Never')
        self.donation_label = QLabel(f"📅 Donation: {last_donation}")
        self.donation_label.setFont(QFont('Arial', 12))
        self.info_layout.addWidget(self.donation_label)
        
        self.sidebar_layout.addWidget(self.info_box)
        self.sidebar_layout.addSpacing(20)
        
        # Navigation Buttons
        nav_buttons = [
            ("📋 Update Donation Date", self.show_update_date),
            ("➕ Create Post", self.show_create_post),
            ("🔐 Change Password", self.change_password),
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
            self.sidebar_layout.addWidget(btn)
        
        self.sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        
        # Right Content Area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f8f9fa;")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(20)
        
        # Content Header
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_header = QLabel("🩸 Donation Posts")
        self.content_header.setFont(QFont('Arial', 20, QFont.Bold))
        self.content_header.setStyleSheet("color: #2c3e50;")
        self.header_layout.addWidget(self.content_header)

        # Add View Toggle Button
        self.view_toggle_btn = QPushButton("📝 View My Posts")
        self.view_toggle_btn.setFont(QFont('Arial', 11))
        self.view_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
        """)
        self.view_toggle_btn.clicked.connect(self.toggle_view)
        self.header_layout.addWidget(self.view_toggle_btn)

        # Remove the duplicate refresh_btn and keep only one:
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFont(QFont('Arial', 11))
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_current_view)  # Connect to load_current_view
        self.header_layout.addWidget(self.refresh_btn)

        self.header_layout.addStretch()
        self.content_layout.addWidget(self.header_widget)
        
        # Posts Container
        self.posts_scroll = QScrollArea()
        self.posts_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        self.posts_widget = QWidget()
        self.posts_layout = QVBoxLayout(self.posts_widget)
        self.posts_layout.setSpacing(15)
        self.posts_scroll.setWidget(self.posts_widget)
        self.posts_scroll.setWidgetResizable(True)
        
        self.content_layout.addWidget(self.posts_scroll)
        main_layout.addWidget(self.content_area, 1)

    def update_sidebar_info(self):
        """Update the sidebar user information"""
        # Update donation label
        last_donation = self.user_info['user_data'].get('last_donation', 'Never')
        self.donation_label.setText(f"📅 Donation: {last_donation}")

    def load_posts(self):
        """Load all donation posts from the database"""
        self.clear_content_area()
        self.content_header.setText("🩸 Donation Posts")
        self.refresh_btn.show()
        
        # Load posts from database
        posts = self.db.get_open_posts()
        
        if not posts:
            no_posts = QLabel("📭 No donation / request posts available at the moment.")
            no_posts.setFont(QFont('Arial', 14))
            no_posts.setStyleSheet("color: #7f8c8d; padding: 40px;")
            no_posts.setAlignment(Qt.AlignCenter)
            self.posts_layout.addWidget(no_posts)
            return
        
        for post in posts:
            self.add_post_widget(post, show_delete=False)
        
        self.posts_layout.addStretch()
    
    def toggle_view(self):
        """Toggle between all posts and user's posts"""
        if self.content_header.text() == "🩸 Donation Posts":
            self.show_my_posts()
            self.view_toggle_btn.setText("🩸 View All Posts")
        else:
            self.load_posts()
            self.view_toggle_btn.setText("📝 View My Posts")

    def load_current_view(self):
        """Load the current view (either all posts or user's posts)"""
        if self.content_header.text() == "🩸 Donation Posts":
            self.load_posts()
        else:
            self.show_my_posts()

    def show_my_posts(self):
        """Show user's own posts with delete option"""
        self.clear_content_area()
        self.content_header.setText("📝 My Posts")
        
        # Load user's posts from database
        posts = self.db.get_user_posts(self.user_id)
        
        if not posts:
            no_posts = QLabel("📭 You haven't created any posts yet.")
            no_posts.setFont(QFont('Arial', 14))
            no_posts.setStyleSheet("color: #7f8c8d; padding: 40px;")
            no_posts.setAlignment(Qt.AlignCenter)
            self.posts_layout.addWidget(no_posts)
            return
        
        # Add posts count
        count_label = QLabel(f"You have {len(posts)} post(s)")
        count_label.setFont(QFont('Arial', 12, QFont.Bold))
        count_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        self.posts_layout.addWidget(count_label)
        
        for post in posts:
            self.add_post_widget(post, show_delete=True)
        
        self.posts_layout.addStretch()
    
    def clear_content_area(self):
        """Clear the content area"""
        for i in reversed(range(self.posts_layout.count())): 
            widget = self.posts_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
            else:
                item = self.posts_layout.itemAt(i)
                if item and item.spacerItem():
                    self.posts_layout.removeItem(item)
    
    def add_post_widget(self, post, show_delete=False):
        """Add a post widget to the layout"""
        post_widget = QFrame()
        post_widget.setFrameShape(QFrame.StyledPanel)
        
        # Set border color based on urgency
        urgency = post.get('urgency', 'medium')
        if urgency == 'high':
            bg_color = "#ffeaea"  # Light red background for high urgency
        elif urgency == 'medium':
            bg_color = "#fff5e6"  # Light orange background for medium urgency
        else:
            bg_color = "#e8f5e9"  # Light green background for low urgency
        
        post_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                padding: 0px;
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)
        
        post_layout = QVBoxLayout(post_widget)
        post_layout.setSpacing(10)
        post_layout.setContentsMargins(20, 20, 20, 20)
        
        # Top row: Title + Status badge
        top_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel(f"<b>{post['user_name']}</b> needs <b>{post['blood_group_needed']}</b> blood")
        title_label.setFont(QFont('Arial', 14, QFont.Bold))
        title_label.setTextFormat(Qt.RichText)
        top_layout.addWidget(title_label)
        
        top_layout.addStretch()
        
        # Status badge (for fulfilled posts)
        status = post.get('status', 'open')
        if status == 'fulfilled':
            status_label = QLabel("✅ FULFILLED")
            status_label.setFont(QFont('Arial', 10, QFont.Bold))
            status_label.setStyleSheet("""
                QLabel {
                    background-color: #27ae60;
                    color: white;
                    border-radius: 12px;
                    padding: 2px 10px;
                }
            """)
            top_layout.addWidget(status_label)
        
        # Urgency badge (only show if not fulfilled)
        if status != 'fulfilled':
            urgency_label = QLabel(urgency.upper())
            urgency_label.setFont(QFont('Arial', 10, QFont.Bold))
            urgency_label.setAlignment(Qt.AlignCenter)
            urgency_label.setFixedHeight(25)
            urgency_label.setFixedWidth(80)
            
            if urgency == 'high':
                urgency_label.setStyleSheet("""
                    QLabel {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 12px;
                        padding: 2px 10px;
                    }
                """)
            elif urgency == 'medium':
                urgency_label.setStyleSheet("""
                    QLabel {
                        background-color: #f39c12;
                        color: white;
                        border-radius: 12px;
                        padding: 2px 10px;
                    }
                """)
            else:
                urgency_label.setStyleSheet("""
                    QLabel {
                        background-color: #27ae60;
                        color: white;
                        border-radius: 12px;
                        padding: 2px 10px;
                    }
                """)
            
            top_layout.addWidget(urgency_label)
        
        post_layout.addLayout(top_layout)
        
        # Add a subtle separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(0,0,0,0.1);")
        separator.setFixedHeight(1)
        post_layout.addWidget(separator)
        
        # Details section
        # Location
        location_label = QLabel(f"📍 <b>Location:</b> {post.get('location', 'N/A')}")
        location_label.setTextFormat(Qt.RichText)
        location_label.setFont(QFont('Arial', 12))
        post_layout.addWidget(location_label)
        
        # Contact
        contact_label = QLabel(f"📞 <b>Contact:</b> {post.get('contact_number', 'N/A')}")
        contact_label.setTextFormat(Qt.RichText)
        contact_label.setFont(QFont('Arial', 12))
        post_layout.addWidget(contact_label)
        
        # Description if available
        if post.get('description'):
            desc_label = QLabel(f"📝 <b>Note:</b> {post.get('description', '')}")
            desc_label.setTextFormat(Qt.RichText)
            desc_label.setFont(QFont('Arial', 12))
            desc_label.setWordWrap(True)
            post_layout.addWidget(desc_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # For user's own posts (show_delete=True)
        if show_delete:
            # Complete button for open posts
            if post.get('status', 'open') == 'open':
                complete_btn = QPushButton("✅Mark Complete")
                complete_btn.setFont(QFont('Arial', 11, QFont.Bold))
                complete_btn.setFixedHeight(35)
                complete_btn.setFixedWidth(200)
                complete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #219653;
                    }
                """)
                complete_btn.clicked.connect(lambda checked, p=post: self.mark_post_complete(p))
                button_layout.addWidget(complete_btn)
            
            # Reopen button for fulfilled posts
            elif post.get('status') == 'fulfilled':
                reopen_btn = QPushButton("🔄 Reopen")
                reopen_btn.setFont(QFont('Arial', 11, QFont.Bold))
                reopen_btn.setFixedHeight(35)
                reopen_btn.setFixedWidth(150)
                reopen_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border: none;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #d68910;
                    }
                """)
                reopen_btn.clicked.connect(lambda checked, p=post: self.mark_post_reopen(p))
                button_layout.addWidget(reopen_btn)
            
            # Delete button for user's own posts
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setFont(QFont('Arial', 11, QFont.Bold))
            delete_btn.setFixedHeight(35)
            delete_btn.setFixedWidth(130)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, p=post: self.delete_post(p))
            button_layout.addWidget(delete_btn)
        
        # Help button if user can help (for all posts view)
        if not show_delete:
            user_bg = self.user_info['user_data']['blood_group']
            if user_bg == post['blood_group_needed'] and post.get('status', 'open') == 'open':
                help_btn = QPushButton("💖 I Can Help!")
                help_btn.setFont(QFont('Arial', 12, QFont.Bold))
                help_btn.setFixedHeight(40)
                help_btn.setFixedWidth(150)
                help_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #219653;
                    }
                """)
                help_btn.clicked.connect(lambda checked, p=post: self.offer_help(p))
                button_layout.addWidget(help_btn)
        
        if button_layout.count() > 1:  # Only add if there are buttons
            post_layout.addLayout(button_layout)
        
        # Bottom row: Date + Spacer
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        # Post date
        date = post.get('created_at', '')[:10]
        if date:
            date_label = QLabel(f"📅 Posted on: {date}")
            date_label.setFont(QFont('Arial', 10))
            date_label.setStyleSheet("color: #666666;")
            bottom_layout.addWidget(date_label)
        
        post_layout.addLayout(bottom_layout)
        
        self.posts_layout.addWidget(post_widget)

    def mark_post_complete(self, post):
        """Mark a post as complete/fulfilled"""
        reply = QMessageBox.question(
            self, 'Mark as Complete',
            f"Are you sure you want to mark this request as complete?\n\n"
            f"🩸 Blood Group: {post['blood_group_needed']}\n"
            f"📍 Location: {post['location']}\n\n"
            f"This will change the status to 'fulfilled'.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Update post status to 'fulfilled'
                post_id = post.get('post_id') or post.get('id')
                self.db.update_post_status(post_id, 'fulfilled')
                
                QMessageBox.information(
                    self, "Success",
                    "✅ Post marked as complete!\n"
                    "Thank you for updating the status."
                )
                # Refresh the my posts view
                self.show_my_posts()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ {str(e)}")

    def mark_post_reopen(self, post):
        """Reopen a fulfilled post"""
        reply = QMessageBox.question(
            self, 'Reopen Post',
            f"Are you sure you want to reopen this request?\n\n"
            f"🩸 Blood Group: {post['blood_group_needed']}\n"
            f"📍 Location: {post['location']}\n\n"
            f"This will change the status back to 'open'.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Update post status to 'open'
                post_id = post.get('post_id') or post.get('id')
                self.db.update_post_status(post_id, 'open')
                
                QMessageBox.information(
                    self, "Success",
                    "✅ Post reopened!\n"
                    "The request is now visible to donors again."
                )
                # Refresh the my posts view
                self.show_my_posts()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ {str(e)}")

    def delete_post(self, post):
        """Delete a post from database"""
        # Ensure post_id exists
        post_id = post.get('post_id') or post.get('id')
        if not post_id:
            QMessageBox.critical(self, "Error", "Cannot delete post: Post ID not found")
            return
        
        status = post.get('status', 'open')
        status_text = "✅ FULFILLED" if status == 'fulfilled' else "🟢 OPEN"
        
        reply = QMessageBox.question(
            self, 'Delete Post',
            f"Are you sure you want to delete this post?\n\n"
            f"🩸 Blood Group: {post['blood_group_needed']}\n"
            f"📍 Location: {post['location']}\n"
            f"Status: {status_text}\n\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_post(post_id)
                QMessageBox.information(
                    self, "Success",
                    "✅ Post deleted successfully!"
                )
                # Refresh the my posts view
                self.show_my_posts()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ {str(e)}")

    def offer_help(self, post):
        """Offer help for a donation request"""
        # Check if post is still open
        if post.get('status') != 'open':
            QMessageBox.warning(
                self, "Cannot Help",
                "⚠️ This request has already been fulfilled and is no longer open."
            )
            return
        
        reply = QMessageBox.question(
            self, 'Offer Help',
            f"💖 Would you like to help {post['user_name']}?\n\n"
            f"📞 Contact: {post['contact_number']}\n"
            f"📍 Location: {post['location']}\n"
            f"🩸 Blood Group Needed: {post['blood_group_needed']}\n\n"
            f"Please contact them directly to arrange donation.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self, "Thank You!",
                "💖 Thank you for your generosity!\n\n"
                "Your willingness to help saves lives. "
                "Please contact the person directly to arrange donation."
            )

    def show_update_date(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Donation Date")
        dialog.setModal(True)
        dialog.setFixedSize(500, 300)  # Reduced height since we removed one field
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Update Donation History")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info text
        info_text = QLabel("Please select the date of your last blood donation.\nNext available date will be automatically set to 90 days later.")
        info_text.setFont(QFont('Arial', 10))
        info_text.setStyleSheet("color: #7f8c8d; padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        info_text.setWordWrap(True)
        info_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_text)
        
        # Last donation date
        last_layout = QVBoxLayout()
        last_label = QLabel("📅 Last Donation Date:")
        last_label.setFont(QFont('Arial', 11, QFont.Bold))
        last_layout.addWidget(last_label)
        
        self.last_date_edit = QDateEdit()
        self.last_date_edit.setCalendarPopup(True)
        
        # Set default date to today
        self.last_date_edit.setDate(QDate.currentDate())
        self.last_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.last_date_edit.setFixedHeight(40)
        self.last_date_edit.setStyleSheet("""
            QDateEdit {
                font-size: 14px;
                padding: 5px;
            }
        """)
        
        # Connect signal to show calculated date
        self.last_date_edit.dateChanged.connect(self.update_next_date_preview)
        last_layout.addWidget(self.last_date_edit)
        layout.addLayout(last_layout)
        
        # Next available date preview (read-only)
        self.next_date_preview = QLabel()
        self.next_date_preview.setFont(QFont('Arial', 11))
        self.next_date_preview.setStyleSheet("color: #27ae60; padding: 5px;")
        self.next_date_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.next_date_preview)
        
        # Update preview with initial date
        self.update_next_date_preview(QDate.currentDate())
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton("💾 Save Donation Date")
        save_btn.setFont(QFont('Arial', 12))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_donation_dates(dialog))
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setFont(QFont('Arial', 12))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()

    def update_next_date_preview(self, selected_date):
        """Update the preview label showing next available date"""
        next_date = selected_date.addDays(90)
        self.next_date_preview.setText(
            f"📅 <b>Next available donation date:</b> {next_date.toString('dd/MM/yyyy')} "
        )

    def save_donation_dates(self, dialog):
        last_date = self.last_date_edit.date().toString("yyyy-MM-dd")
        next_date = self.last_date_edit.date().addDays(90).toString("yyyy-MM-dd")
        
        try:
            self.db.update_user(self.user_id, {
                'last_donation': last_date,
                'next_available': next_date
            })
            
            # Update user info locally
            self.user_info['user_data']['last_donation'] = last_date
            self.user_info['user_data']['next_available'] = next_date
            
            # Update sidebar display immediately
            self.update_sidebar_info()
            
            QMessageBox.information(
                self, "Success", 
                "✅ Donation date updated successfully!\n\n"
                f"Last donation: {last_date}\n"
                f"Next available: {next_date}\n\n"
                "Thank you for updating your donation history!"
            )
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ {str(e)}")

    def delete_post(self, post):
        """Delete a post from database"""
        # Ensure post_id exists
        post_id = post.get('post_id') or post.get('id')
        if not post_id:
            QMessageBox.critical(self, "Error", "Cannot delete post: Post ID not found")
            return
        
        reply = QMessageBox.question(
            self, 'Delete Post',
            f"Are you sure you want to delete this post?\n\n"
            f"🩸 Blood Group: {post['blood_group_needed']}\n"
            f"📍 Location: {post['location']}\n\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_post(post_id)
                QMessageBox.information(
                    self, "Success",
                    "✅ Post deleted successfully!"
                )
                # Refresh the my posts view
                self.show_my_posts()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ {str(e)}")

    def show_create_post(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Donation Request")
        dialog.setModal(True)
        dialog.setFixedSize(500, 550)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Create New Donation Request")
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)
        
        # Blood Group Needed
        blood_layout = QHBoxLayout()
        blood_label = QLabel("🩸 Blood Group Needed:")
        blood_label.setFont(QFont('Arial', 11, QFont.Bold))
        blood_layout.addWidget(blood_label)
        
        self.post_blood_combo = QComboBox()
        self.post_blood_combo.addItems(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        self.post_blood_combo.setFont(QFont('Arial', 12))
        blood_layout.addWidget(self.post_blood_combo)
        form_layout.addLayout(blood_layout)
        
        # Location
        location_layout = QHBoxLayout()
        location_label = QLabel("📍 Location:")
        location_label.setFont(QFont('Arial', 11, QFont.Bold))
        location_layout.addWidget(location_label)
        
        self.post_location_input = QLineEdit()
        self.post_location_input.setFont(QFont('Arial', 12))
        self.post_location_input.setText(self.user_info['user_data']['location'])
        location_layout.addWidget(self.post_location_input)
        form_layout.addLayout(location_layout)
        
        # Contact
        contact_layout = QHBoxLayout()
        contact_label = QLabel("📞 Contact Number:")
        contact_label.setFont(QFont('Arial', 11, QFont.Bold))
        contact_layout.addWidget(contact_label)
        
        self.post_contact_input = QLineEdit()
        self.post_contact_input.setFont(QFont('Arial', 12))
        self.post_contact_input.setText(self.user_info['user_data']['contact_number'])
        contact_layout.addWidget(self.post_contact_input)
        form_layout.addLayout(contact_layout)
        
        # Urgency
        urgency_layout = QHBoxLayout()
        urgency_label = QLabel("⚠️ Urgency Level:")
        urgency_label.setFont(QFont('Arial', 11, QFont.Bold))
        urgency_layout.addWidget(urgency_label)
        
        self.post_urgency_combo = QComboBox()
        self.post_urgency_combo.addItems(["high (Critical)", "medium (Urgent)", "low (Normal)"])
        self.post_urgency_combo.setFont(QFont('Arial', 12))
        urgency_layout.addWidget(self.post_urgency_combo)
        form_layout.addLayout(urgency_layout)
        
        # Description
        desc_label = QLabel("📝 Additional Information:")
        desc_label.setFont(QFont('Arial', 11, QFont.Bold))
        form_layout.addWidget(desc_label)
        
        self.post_desc_input = QTextEdit()
        self.post_desc_input.setFont(QFont('Arial', 12))
        self.post_desc_input.setPlaceholderText("Enter any additional details (e.g., hospital name, patient condition, etc.)")
        self.post_desc_input.setMaximumHeight(100)
        form_layout.addWidget(self.post_desc_input)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        create_btn = QPushButton("➕ Create Post")
        create_btn.setFont(QFont('Arial', 12, QFont.Bold))
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 30px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        create_btn.clicked.connect(lambda: self.create_post(dialog))
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setFont(QFont('Arial', 12))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 30px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def create_post(self, dialog):
        # Extract urgency level from combo box
        urgency_text = self.post_urgency_combo.currentText()
        urgency = urgency_text.split(' ')[0].lower()  # Get "high", "medium", or "low"
        
        post = Post(
            user_id=self.user_id,
            user_name=self.user_info['user_data']['name'],
            blood_group_needed=self.post_blood_combo.currentText(),
            location=self.post_location_input.text().strip(),
            contact_number=self.post_contact_input.text().strip(),
            urgency=urgency,
            description=self.post_desc_input.toPlainText().strip()
        )
        
        # Validation
        if not post.location:
            QMessageBox.warning(self, "Warning", "📍 Please enter location!")
            return
        
        if not post.contact_number:
            QMessageBox.warning(self, "Warning", "📞 Please enter contact number!")
            return
        
        try:
            post_id = self.db.create_post(post)
            QMessageBox.information(self, "Success", 
                                  "✅ Post created successfully!\n"
                                  "Your request is now visible to potential donors.")
            self.load_posts()  # Refresh posts
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ {str(e)}")
    
    def change_password(self):
        email = self.user_info['user_data']['email']
        try:
            self.db.reset_password(email)
            QMessageBox.information(
                self, "Password Reset",
                "📧 Password reset link has been sent to your email!\n\n"
                "Please check your inbox and follow the instructions."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ {str(e)}")
    
    def logout(self):
        """Logout method - emits signal"""
        print("UserWindow: Logout clicked")
        self.logout_signal.emit()
        self.close()