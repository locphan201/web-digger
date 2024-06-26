from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout

class IndexingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        v_layout = QVBoxLayout()
        label = QLabel('Coming soon')
        v_layout.addWidget(label)
        self.setLayout(v_layout)
