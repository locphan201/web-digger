import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from pages.recursive_page import RecursivePage
from pages.indexing_page import IndexingPage
from pages.tutorial_page import TutorialPage

'''
    WEB DIGGER
    VERSION 26.06.2024
'''

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Web Digger - v26.06.2024')
        self.setGeometry(100, 100, 800, 600)

        # Create the tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(RecursivePage(), 'Recursive')
        self.tabs.addTab(IndexingPage(), 'Indexing')
        self.tabs.addTab(TutorialPage(), 'Tutorial')

def main():
    app = QApplication(sys.argv)
    main_window = MainApplication()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
