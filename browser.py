import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit,
    QPushButton, QTabWidget, QMessageBox, QComboBox, QColorDialog, QFileDialog, QMenu
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spectra")
        self.setGeometry(100, 100, 1200, 800)

        # Default background settings
        self.default_bg_color = "white"
        self.google_bg_color = None
        self.google_bg_image = None

        # Create navigation layout first
        self.nav_bar = self.create_nav_bar()

        # Create the tab widget to manage multiple tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_address_bar)

        # Add the first tab
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

        # Set the central widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.nav_bar)
        main_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_nav_bar(self):
        """Create the navigation bar with buttons, address bar, and theme selector."""
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL")
        self.address_bar.returnPressed.connect(self.navigate_to_url)

        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("icons/backward.png"))
        self.back_button.clicked.connect(self.browser_back)

        self.forward_button = QPushButton()
        self.forward_button.setIcon(QIcon("icons/forward.png"))
        self.forward_button.clicked.connect(self.browser_forward)

        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon("icons/refresh.png"))
        self.refresh_button.clicked.connect(self.browser_refresh)

        self.new_tab_button = QPushButton()
        self.new_tab_button.setIcon(QIcon("icons/plus.png"))  # Add an icon for new tab
        self.new_tab_button.clicked.connect(self.open_new_tab)

        # Theme selector
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Default (White)", "Dark (Black)", "Soft Blue", "Light Gray"])
        self.theme_selector.currentIndexChanged.connect(self.change_theme)

        # Customize button with dropdown menu
        self.customize_button = QPushButton("Customize")
        self.customize_menu = QMenu()

        self.bg_color_action = self.customize_menu.addAction("Set Google BG Color")
        self.bg_color_action.triggered.connect(self.set_google_bg_color)

        self.bg_image_action = self.customize_menu.addAction("Set Google BG Image")
        self.bg_image_action.triggered.connect(self.set_google_bg_image)

        self.customize_button.setMenu(self.customize_menu)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.refresh_button)
        nav_layout.addWidget(self.address_bar)
        nav_layout.addWidget(self.new_tab_button)
        nav_layout.addWidget(self.theme_selector)
        nav_layout.addWidget(self.customize_button)

        nav_container = QWidget()
        nav_container.setLayout(nav_layout)
        return nav_container

    def add_new_tab(self, qurl=None, label="New Tab"):
        """Add a new tab with a web view."""
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.urlChanged.connect(lambda qurl: self.update_address_bar_for_tab(browser))

        # Apply custom background if the page is Google
        browser.loadFinished.connect(lambda: self.apply_google_custom_bg(browser))

        i = self.tabs.addTab(browser, label)
        self.tabs.setTabIcon(i, QIcon("icons/tab.png"))  # Optional: add an icon to the tab
        self.tabs.setCurrentIndex(i)

    def open_new_tab(self):
        """Open a new tab with the Google search engine."""
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

    def close_tab(self, index):
        """Close the tab at the given index."""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.show_warning("Cannot close the last tab.")

    def update_address_bar(self, index):
        """Update the address bar when the tab changes."""
        current_browser = self.tabs.widget(index)
        if current_browser:
            self.address_bar.setText(current_browser.url().toString())

    def update_address_bar_for_tab(self, browser):
        """Update the address bar for the current tab."""
        if browser == self.tabs.currentWidget():
            self.address_bar.setText(browser.url().toString())

    def navigate_to_url(self):
        """Navigate to the URL entered in the address bar."""
        url = self.address_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.tabs.currentWidget().setUrl(QUrl(url))

    def browser_back(self):
        """Navigate to the previous page in the current tab's history."""
        current_browser = self.tabs.currentWidget()
        if current_browser and current_browser.history().canGoBack():
            current_browser.back()

    def browser_forward(self):
        """Navigate to the next page in the current tab's history."""
        current_browser = self.tabs.currentWidget()
        if current_browser and current_browser.history().canGoForward():
            current_browser.forward()

    def browser_refresh(self):
        """Reload the current page in the current tab."""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.reload()

    def change_theme(self):
        """Change the background theme based on user selection."""
        theme = self.theme_selector.currentText()
        if theme == "Default (White)":
            self.setStyleSheet("background-color: white;")
        elif theme == "Dark (Black)":
            self.setStyleSheet("background-color: black; color: white;")
        elif theme == "Soft Blue":
            self.setStyleSheet("background-color: #add8e6;")
        elif theme == "Light Gray":
            self.setStyleSheet("background-color: #d3d3d3;")

    def set_google_bg_color(self):
        """Open a color picker to select a background color for Google."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.google_bg_color = color.name()
            self.apply_google_custom_bg(self.tabs.currentWidget())

    def set_google_bg_image(self):
        """Open a file dialog to select a background image for Google."""
        # Open file dialog to select an image file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # Save the file path and apply the background
            self.google_bg_image = file_path.replace("\\", "/")  # Replace backslashes with forward slashes for JS compatibility
            self.apply_google_custom_bg(self.tabs.currentWidget())

    def apply_google_custom_bg(self, browser):
        """Apply a custom background to the Google search engine page."""
        if browser.url().host() == "www.google.com":
            # JavaScript to apply background settings
            script = """
                try {{
                    document.body.style.backgroundColor = '{bg_color}';
                    document.body.style.backgroundImage = "url('file://{bg_image}')";
                    document.body.style.backgroundSize = 'cover';
                    document.body.style.backgroundRepeat = 'no-repeat';
                }} catch (error) {{
                    console.error('Error applying background:', error);
                }}
            """.format(
                bg_color=self.google_bg_color if hasattr(self, "google_bg_color") and self.google_bg_color else "#ffffff",
                bg_image=self.google_bg_image if hasattr(self, "google_bg_image") and self.google_bg_image else ""
            )
            # Execute the JavaScript in the current browser tab
            browser.page().runJavaScript(script)
        else:
            print("Background can only be applied to www.google.com")

        def show_warning(self, message):
            """Display a warning message."""
            QMessageBox.warning(self, "Warning", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Ensure icons are loaded properly
    # Icons should be located in an "icons" folder relative to the script
    window = Browser()
    window.show()
    sys.exit(app.exec_())
