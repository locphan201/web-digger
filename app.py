import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy, QLabel
from PyQt5.QtCore import QUrl
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

OUTPUT = 'output'
os.makedirs(OUTPUT, exist_ok=True)

class WebScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.url_queue = []
        self.visited_urls = set()
        self.is_running = False

        # Initialize the main window
        self.setWindowTitle('Recursive Scraper')
        self.setGeometry(100, 100, 800, 600)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Input URL
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText('Enter URL here...')
        self.url_input.textChanged.connect(self.validate_url)
        layout.addWidget(self.url_input)

        # Progress and Status
        status_counter_layout = QHBoxLayout()
        self.status_label = QLabel('Status: Idle')
        status_counter_layout.addWidget(self.status_label)

        self.remaining_label = QLabel('URLs remaining: 0')
        status_counter_layout.addWidget(self.remaining_label)

        self.url_count_label = QLabel('Valid URLs found: 0')
        status_counter_layout.addWidget(self.url_count_label)
        layout.addLayout(status_counter_layout)

        # Text Area for Logs
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # Horizontal Layout for Buttons
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)

        # Cancel Button
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)

        # Export Button
        self.export_button = QPushButton('Export', self)
        self.export_button.clicked.connect(self.export)
        button_layout.addWidget(self.export_button)

        # Execute Button
        self.execute_button = QPushButton('Execute', self)
        self.execute_button.clicked.connect(self.execute)
        self.execute_button.setEnabled(False)
        button_layout.addWidget(self.execute_button)

        layout.addLayout(button_layout)

    def validate_url(self):
        url_text = self.url_input.text()
        valid_url = QUrl(url_text).isValid() and url_text.strip() != ''
        self.execute_button.setEnabled(valid_url)

    def find_urls(self, base_url):
        self.url_queue.append(base_url)
        self.visited_urls.add(base_url)
        self.is_running = True
        self.cancel_button.setEnabled(True)
        self.status_label.setText('Status: Running')
        self.update_remaining_count()

        self.log_area.append('\n\n')

        while self.url_queue and self.is_running:
            current_url = self.url_queue.pop(0)
            self.log_area.append(f'Processing: {current_url}')
            self.update_remaining_count()
            QApplication.processEvents()

            try:
                response = requests.get(current_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                a_tags = soup.find_all('a')
                for a_tag in a_tags:
                    href = a_tag.get('href')
                    if '#' in href or not href:
                        continue
                    if href and href.startswith('/'):
                        href = urljoin(current_url, href)
                    if href and href not in self.visited_urls:
                        self.visited_urls.add(href)
                        self.url_queue.append(href)
                        self.log_area.append(href)
                        self.update_url_count()
            except Exception as e:
                self.log_area.append(f'Error: {e}')
            QApplication.processEvents()

        self.is_running = False
        self.cancel_button.setEnabled(False)
        self.status_label.setText('Status: Complete')

    def update_url_count(self):
        self.url_count_label.setText(f'Valid URLs found: {len(self.visited_urls)}')

    def update_remaining_count(self):
        self.remaining_label.setText(f'URLs remaining: {len(self.url_queue)}')

    def execute(self):
        url = self.url_input.text()
        self.execute_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.find_urls(url)
        self.execute_button.setEnabled(True)
        self.export_button.setEnabled(True)

    def cancel(self):
        self.is_running = False
        self.cancel_button.setEnabled(False)
        self.status_label.setText('Status: Cancelled')

    def export(self):
        if self.visited_urls:
            first_url = next(iter(self.visited_urls))

            parsed_url = urlparse(first_url)
            domain = parsed_url.netloc

            os.makedirs(os.path.join('OUTPUT', domain), exist_ok=True)
            output_dir = os.path.join('OUTPUT', domain, 'urls.txt')

            with open(output_dir, 'w', encoding='utf-8') as file:
                file.writelines(f'{url}\n' for url in sorted(self.visited_urls))
            
            self.log_area.append(f"\nExported as '{output_dir}'")
        else:
            self.log_area.append('\nNo URLs to Export')

def main():
    app = QApplication(sys.argv)
    gui = WebScraperGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
