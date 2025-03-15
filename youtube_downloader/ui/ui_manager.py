# ui/ui_manager.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QComboBox, QFileDialog, QProgressBar, QListWidget, QListWidgetItem,
    QCheckBox, QMenu, QMenuBar, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

class UIManager(QWidget):
    search_requested = pyqtSignal(str)
    download_requested = pyqtSignal(str, str)  # url, quality
    cancel_requested = pyqtSignal()
    path_browse_requested = pyqtSignal()
    theme_change_requested = pyqtSignal(bool) # is_dark_mode
    help_user_requested =  pyqtSignal()
    help_dev_requested =  pyqtSignal()
    about_requested = pyqtSignal()
    system_exit_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dark_mode = True # Default

        # Initialize all UI components as instance variables
        self.url_input = QLineEdit()
        self.search_button = QPushButton(qta.icon("fa5s.search"), "Search")
        self.results_list = QListWidget()
        self.total_results_label = QLabel("")
        self.video_info = QLabel("No video selected yet")
        self.quality_combo = QComboBox()
        self.audio_only = QCheckBox("Download audio only")
        self.path_label = QLabel("")  # Will be set later
        self.browse_button = QPushButton(qta.icon("fa5s.folder-open"), "Browse...")
        self.download_button = QPushButton(qta.icon("fa5s.download"), "Download")
        self.cancel_button = QPushButton(qta.icon("fa5s.times-circle"), "Cancel")
        self.progress = QProgressBar()
        

        self.status_label = QLabel("Ready")
        self.dark_mode_check = QCheckBox("Dark mode")
        self.menu_bar = QMenuBar()

        self.setup_ui()  # Initialize the UI

    def setup_ui(self):
        # --- Main Layout ---
        layout = QVBoxLayout(self)
        
         # --- Menu Bar ---
        self.setup_menu_bar()
        layout.addWidget(self.menu_bar)

        # --- Search Section ---
        search_layout = QHBoxLayout()
        self.url_input.setPlaceholderText("Enter YouTube URL or search keywords...")
        self.search_button.setToolTip("Search for videos")
        search_layout.addWidget(self.url_input, 4)
        search_layout.addWidget(self.search_button, 1)
        layout.addLayout(search_layout)

        # --- Results List ---
        self.results_list.setMinimumHeight(200)
        layout.addWidget(QLabel("Search results:"))
        layout.addWidget(self.results_list)
        layout.addWidget(self.total_results_label)

        # --- Selected Video Info ---
        layout.addWidget(self.video_info)

        # --- Download Options ---
        download_options_group = QWidget()
        download_options_layout = QHBoxLayout(download_options_group)

        # Quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Video quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.sizeAdjustPolicy()
        quality_layout.addWidget(self.quality_combo)
        download_options_layout.addLayout(quality_layout)

        # Audio Only
        download_options_layout.addStretch() # Add a stretch to push the checkbox to the right
        self.audio_only = QCheckBox("Download audio only")
        self.audio_only.stateChanged.connect(self.update_quality_options)
        download_options_layout.addWidget(self.audio_only)

        layout.addWidget(download_options_group)

        # --- Save Location ---
        save_location_group = QWidget()
        save_location_layout = QHBoxLayout(save_location_group)
        save_location_layout.addWidget(self.path_label)
        save_location_layout.addWidget(self.browse_button)
        layout.addWidget(save_location_group)
        

        # --- Download/Cancel Buttons ---
        download_buttons_layout = QHBoxLayout()
        self.download_button.setMinimumHeight(50)
        self.download_button.setEnabled(False)
        self.download_button.setToolTip("Start download")
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setToolTip("Cancel download")
        download_buttons_layout.addWidget(self.download_button)
        download_buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(download_buttons_layout)

        # --- Progress Bar & Status ---
        layout.addWidget(self.progress)

        # --- Status and Dark Mode ---
        status_theme_layout = QHBoxLayout()
        status_theme_layout.addWidget(self.status_label)
        status_theme_layout.addStretch()  # Stretch to push dark mode to the right
        status_theme_layout.addWidget(self.dark_mode_check)
        layout.addLayout(status_theme_layout)

        # --- Connections ---
        self.search_button.clicked.connect(self.on_search_clicked)
        self.browse_button.clicked.connect(self.path_browse_requested)  
        self.download_button.clicked.connect(self.on_download_clicked)
        self.cancel_button.clicked.connect(self.cancel_requested)  
        self.dark_mode_check.stateChanged.connect(self.on_theme_change_requested)
        self.results_list.itemClicked.connect(self.on_item_selected)

    def setup_menu_bar(self):
        # Help Menu
        
        help_menu = QMenu("&Help", self)
        help_action_user = help_menu.addAction(qta.icon("fa5s.question-circle"), "&User Guide")
        help_action_user.triggered.connect(self.help_user_requested)

        help_action_dev = help_menu.addAction(qta.icon("fa5s.file-code"), "&Developer Guide")
        help_action_dev.triggered.connect(self.help_dev_requested)
        
        # About Menu
        about_menu = QMenu("&About", self)
        about_action = about_menu.addAction(qta.icon("fa5s.info-circle"), "&Software Information")
        about_action.triggered.connect(self.about_requested)

        # System Menu
        system_menu = QMenu("&System", self)
        system_action_exit = system_menu.addAction(qta.icon("fa5s.sign-out-alt"), "&Exit application")
        system_action_exit.triggered.connect(self.system_exit_requested)
        
        self.menu_bar.addMenu(system_menu)
        self.menu_bar.addMenu(help_menu)
        self.menu_bar.addMenu(about_menu)
        
        
    def on_search_clicked(self):
        query = self.url_input.text().strip()
        if query:  # Only emit if there's a query
            self.search_requested.emit(query)
        
        

    def on_download_clicked(self):
        """Emits download request signal with user-selected video info."""
        selected_item = self.results_list.currentItem()
        if selected_item:
            video_info = selected_item.data(Qt.ItemDataRole.UserRole)
            url = video_info['url']
            quality = self.quality_combo.currentText()
            if self.audio_only.isChecked():
                quality = "bestaudio"

            self.download_requested.emit(url, quality)  # Emit only URL & Quality


    def on_theme_change_requested(self, state):
        is_dark_mode = state == Qt.CheckState.Checked.value
        self.theme_change_requested.emit(is_dark_mode)

    def on_item_selected(self, item):
        """Handles item selection in the results list."""
        # The item is selected, so enable the download button.  The actual
        # population of the quality options is handled in the AppController,
        # triggered by the selection_changed signal.
        self.download_button.setEnabled(True)

        # Display the video info in the UI
        video_info = item.data(Qt.ItemDataRole.UserRole)
        if video_info:
            self.video_info.setText(
                f"Selected: {video_info['title']} ({video_info['duration']})"
            )


    def update_quality_options(self):
        """Enable/disable quality selection based on audio-only checkbox."""
        self.quality_combo.setEnabled(not self.audio_only.isChecked())


    def set_dark_mode(self, is_dark_mode):
        """Applies the dark or light theme."""
        self.dark_mode = is_dark_mode
        if is_dark_mode:
            self.setStyleSheet(self._dark_mode_stylesheet())
        else:
            self.setStyleSheet(self._light_mode_stylesheet())

        # Force UI refresh
        QApplication.instance().setStyleSheet("")
        QApplication.instance().setStyleSheet(self.styleSheet())
        self.update()

    def _dark_mode_stylesheet(self):
        return """
           QWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                font-size: 10pt;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #3D3D3D;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #0078D7;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0078D7;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1C86E0;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
            QProgressBar {
                text-align: center;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #3D3D3D;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                border-radius: 3px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
            }
            QMenuBar {
                background-color: #3D3D3D;
                color: #FFFFFF;
            }
            QMenu {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #555555;
            }
            QMenu::item:selected {
                background-color: #0078D7;
            }
        """

    def _light_mode_stylesheet(self):
        return """
           QWidget {
                background-color: #F0F0F0;
                color: #333333;
                font-size: 10pt;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #0078D7;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0078D7;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1C86E0;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
            QProgressBar {
                text-align: center;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                border-radius: 3px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
            QMenuBar {
                background-color: #F0F0F0;
                color: #333333;
            }

            QMenu {
                background-color: #F0F0F0;
                color: #333333;
                border: 1px solid #CCCCCC;
            }

            QMenu::item:selected {
                background-color: #0078D7;
            }
        """

    # --- Methods to update the UI (called by AppController) ---

    def display_results(self, results):
        """Displays search results in the list."""
        self.results_list.clear()
        for i, video in enumerate(results):
            item = QListWidgetItem(
                f"{i+1}. {video['title']} ({video['duration']})"
            )
            item.setData(Qt.ItemDataRole.UserRole, video)
            item.setToolTip(f"URL: {video['url']}")
            self.results_list.addItem(item)
        self.total_results_label.setText(f"Total results: {len(results)}")

    def clear_results(self):
        self.results_list.clear()
        self.total_results_label.setText("")

    def set_progress_value(self, value):
        self.progress.setValue(value)

    def set_save_path(self, path):
        self.path_label.setText(f"Save to: {path}")

    def populate_quality_combo(self, video_info):
        """Populates the quality combo box with formats from video_info."""
        self.quality_combo.clear()
        formats = video_info.get('formats', [])
        available_formats = []
        for f in formats:
            if f.get('ext') == 'mp4' and 'height' in f:
                available_formats.append(f"{f['height']}p")

        if not available_formats:
            available_formats = ["720p", "1080p", "1440p", "2160p"]
            if self.audio_only.isChecked():
               available_formats = ["bestaudio"]

        self.quality_combo.addItems(
            sorted(list(set(available_formats)), key=lambda x: int(x[:-1]) if x.endswith('p') else 0, reverse=True)
        )
        self.quality_combo.setEnabled(not self.audio_only.isChecked())
    
    def show_message(self, title, message):
        """Displays an informational message box."""
        QMessageBox.information(self, title, message)

    def show_error(self, title, message):
        """Displays an error message box."""
        QMessageBox.critical(self, title, message)
        
    def set_status_message(self, message):
        self.status_label.setText(message)