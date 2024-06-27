from PyQt5.QtWidgets import (
    QApplication, QPushButton, QProgressBar, QLineEdit, 
    QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, 
    QSpacerItem, QSizePolicy, QLabel
)
from PyQt5.QtCore import QUrl
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

# Configuration
OUTPUT = 'output'
os.makedirs(OUTPUT, exist_ok=True)

class IndexingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.visited_urls = set()
        self.is_running = False
        self.range_min = 1
        self.range_max = 20
        self.current_index = 1

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText('Enter URL here...')
        self.url_input.textChanged.connect(self.validate_url)
        layout.addWidget(self.url_input)

        # Progress and Status
        status_counter_layout = QHBoxLayout()
        self.status_label = QLabel('Status: Idle')
        status_counter_layout.addWidget(self.status_label)

        self.index_label = QLabel('Index: 0')
        status_counter_layout.addWidget(self.index_label)

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
        if len(self.visited_urls) != 0:
            self.log_area.append(f'\n{"*" * 25}\n')
        self.visited_urls = set()
        self.is_running = False
        self.range_min = 0
        self.range_max = 0
        self.current_index = 0
        self.update_index_count()
        self.update_url_count()
        self.update_progress_bar()

    def update_progress_bar(self):
        '''
            Update the progress bar
        '''
        if self.range_max == 0:
            progress = 50
        else:
            progress = self.current_index / self.range_max * 100
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
            Indexing scrap a website
        '''
        self.is_running = True
        self.status_label.setText('Status: Running')
        self.update_index_count()

        while self.is_running:
            if self.range_max > 0 and self.range_max < self.current_index:
                break
            
            if not '{index}' in base_url:
                self.log_area.append('Base URL DOES NOT contain {index} for indexing')
                break

            current_url = base_url.format(index=self.current_index)
            self.update_index_count()
            QApplication.processEvents()

            try:
                response = requests.get(current_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                articles = soup.find_all('article')
                for article in articles:
                    a_tag = article.find('a')
                    if a_tag:
                        href = a_tag.get('href')
                        if href:
                            self.visited_urls.add(href)
                            self.log_area.append(href)
                            self.update_url_count()
                            self.update_progress_bar()
            except Exception as e:
                self.log_area.append(f'Error: {e}')

            self.current_index += 1
            QApplication.processEvents()

        self.log_area.append('\nFinished')
        self.is_running = False
        self.status_label.setText('Status: Complete')

    def update_url_count(self):
        self.url_count_label.setText(f'Valid URLs found: {len(self.visited_urls)}') # Show valid URLs

    def update_index_count(self):
        self.index_label.setText(f'Index: {self.current_index}') # Show page index

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
            output_dir = os.path.join('OUTPUT', domain, 'indexing_urls.txt')

            with open(output_dir, 'w', encoding='utf-8') as file:
                file.writelines(f'{url}\n' for url in sorted(self.visited_urls))
            
            self.log_area.append(f"\nExported as '{output_dir}'")
        else:
            self.log_area.append('\nNo URLs to Export')