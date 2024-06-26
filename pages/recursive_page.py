from PyQt5.QtWidgets import (
    QApplication, QPushButton, QProgressBar, QLineEdit, 
    QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, 
    QSpacerItem, QSizePolicy, QLabel, QComboBox
)
from PyQt5.QtCore import QUrl
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

# Configuration
OUTPUT = 'output'
os.makedirs(OUTPUT, exist_ok=True)

class RecursivePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Initialize variables
        self.url_queue = []
        self.visited_urls = set()
        self.is_running = False
        self.visit_limit = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText('Enter URL here...')
        self.url_input.textChanged.connect(self.validate_url)
        top_layout.addWidget(self.url_input)

        # Combo Box for limit selection
        self.limit_combo = QComboBox(self)
        self.limit_combo.addItem('Unlimited', None)
        for i in range(1, 11):  # Add options up to 10,000
            self.limit_combo.addItem(f'{i * 1000} items', i * 1000)
        self.limit_combo.currentIndexChanged.connect(self.set_limit)
        top_layout.addWidget(self.limit_combo)
        layout.addLayout(top_layout)

        # Progress and Status
        status_counter_layout = QHBoxLayout()
        self.status_label = QLabel('Status: Idle')
        status_counter_layout.addWidget(self.status_label)

        self.remaining_label = QLabel('URLs remaining: 0')
        status_counter_layout.addWidget(self.remaining_label)

        self.url_count_label = QLabel('Valid URLs found: 0')
        status_counter_layout.addWidget(self.url_count_label)
        layout.addLayout(status_counter_layout)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Text Area for Logs
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # Horizontal Layout for Buttons
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)

        # Reset Button
        self.reset_button = QPushButton('Reset', self)
        self.reset_button.clicked.connect(self.reset)
        button_layout.addWidget(self.reset_button)

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

    def reset(self):
        '''
            Reset the variables
        '''
        if len(self.url_queue) != 0 or len(self.visited_urls) != 0:
            self.log_area.append(f'\n{"*" * 25}\n')
        self.url_queue = []
        self.visited_urls = set()
        self.is_running = False
        self.update_remaining_count()
        self.update_url_count()
        self.update_progress_bar()

    def set_limit(self):
        # Set the visit limit based on combo box selection
        self.visit_limit = self.limit_combo.currentData()

    def update_progress_bar(self):
        '''
            Update the progress bar
        '''
        total_urls = len(self.visited_urls) + len(self.url_queue)
        if not self.visit_limit is None:
            total_urls = self.visit_limit
        if total_urls > 0:
            progress = len(self.visited_urls) / total_urls * 100
        else:
            progress = 0
        self.progress_bar.setValue(int(progress))

    def validate_url(self):
        '''
            Validate the input URL
        '''
        url_text = self.url_input.text()
        valid_url = QUrl(url_text).isValid() and url_text.strip() != ''
        self.execute_button.setEnabled(valid_url)

    def find_urls(self, base_url):
        '''
            Recursive scrap a website
        '''
        self.url_queue.append(base_url)
        self.visited_urls.add(base_url)
        self.is_running = True
        self.status_label.setText('Status: Running')
        self.update_remaining_count()

        self.log_area.append('\n\n')

        while self.url_queue and self.is_running:
            if not self.visit_limit is None and len(self.visited_urls) >= self.visit_limit:
                break

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
                    if not href[0] in '.h/':
                        continue
                    if href.startswith('/'):
                        href = urljoin(current_url, href)
                    if href not in self.visited_urls:
                        self.visited_urls.add(href)
                        self.url_queue.append(href)
                        self.log_area.append(href)
                        self.update_url_count()
                        self.update_progress_bar()
            except Exception as e:
                self.log_area.append(f'Error: {e}')
            QApplication.processEvents()

        self.log_area.append('\nFinished')
        self.is_running = False
        self.status_label.setText('Status: Complete')

    def update_url_count(self):
        self.url_count_label.setText(f'Valid URLs found: {len(self.visited_urls)}') # Show valid URLs

    def update_remaining_count(self):
        self.remaining_label.setText(f'URLs remaining: {len(self.url_queue)}') # Show remaining URLs to check

    def execute(self):
        '''
            Execute scraping procedure
        '''
        url = self.url_input.text()
        # Disable buttons
        self.execute_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        # Start the process
        self.find_urls(url)

        # Enable buttons
        self.execute_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def cancel(self):
        '''
            Stop the scrapping process
        '''
        self.is_running = False
        self.cancel_button.setEnabled(False)
        self.status_label.setText('Status: Cancelled')

    def export(self):
        '''
            Export the valid URLs as .txt file
        '''
        if self.visited_urls:
            url = self.url_input.text()
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            # Save URLs inside the folder named the same as the domain
            os.makedirs(os.path.join('OUTPUT', domain), exist_ok=True)
            output_dir = os.path.join('OUTPUT', domain, 'urls.txt')

            with open(output_dir, 'w', encoding='utf-8') as file:
                file.writelines(f'{url}\n' for url in sorted(self.visited_urls))
            
            self.log_area.append(f"\nExported as '{output_dir}'")
        else:
            self.log_area.append('\nNo URLs to Export')