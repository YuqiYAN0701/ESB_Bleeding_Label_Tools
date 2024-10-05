import sys
import os
import glob
import pandas as pd
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, \
    QTextEdit, QLineEdit
from PySide6.QtGui import QPixmap


class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Viewer')
        self.showFullScreen()

        # Layouts
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left side components
        self.left_image_label = QLabel(self)
        self.left_image_label.setFixedSize(self.width() // 2, self.height() // 2)
        self.left_image_label.setStyleSheet("border: 1px solid black;")
        self.left_filename_edit = QLineEdit(self)
        self.left_text_edit = QTextEdit(self)
        self.left_text_edit.setFixedHeight(200)
        self.left_buttons_layout = QHBoxLayout()
        self.left_prev_button = QPushButton('<-', self)
        self.left_import_button = QPushButton('Import', self)
        self.left_next_button = QPushButton('->', self)
        self.left_buttons_layout.addWidget(self.left_prev_button)
        self.left_buttons_layout.addWidget(self.left_import_button)
        self.left_buttons_layout.addWidget(self.left_next_button)

        left_layout.addWidget(self.left_image_label)
        left_layout.addWidget(self.left_filename_edit)
        left_layout.addWidget(self.left_text_edit)
        left_layout.addLayout(self.left_buttons_layout)

        # Right side components
        self.right_image_label = QLabel(self)
        self.right_image_label.setFixedSize(self.width() // 2, self.height() // 2)
        self.right_image_label.setStyleSheet("border: 1px solid black;")
        self.right_filename_edit = QLineEdit(self)
        self.right_text_edit = QTextEdit(self)
        self.right_text_edit.setFixedHeight(200)
        self.right_buttons_layout = QHBoxLayout()
        self.right_prev_button = QPushButton('<-', self)
        self.right_import_button = QPushButton('Import', self)
        self.right_save_button = QPushButton('Save', self)
        self.right_next_button = QPushButton('->', self)
        self.right_buttons_layout.addWidget(self.right_prev_button)
        self.right_buttons_layout.addWidget(self.right_import_button)
        self.right_buttons_layout.addWidget(self.right_save_button)
        self.right_buttons_layout.addWidget(self.right_next_button)

        right_layout.addWidget(self.right_image_label)
        right_layout.addWidget(self.right_filename_edit)
        right_layout.addWidget(self.right_text_edit)
        right_layout.addLayout(self.right_buttons_layout)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        # Connect buttons
        self.left_import_button.clicked.connect(lambda: self.import_images('left'))
        self.right_import_button.clicked.connect(lambda: self.import_images('right'))
        self.left_prev_button.clicked.connect(lambda: self.change_image('left', -1))
        self.left_next_button.clicked.connect(lambda: self.change_image('left', 1))
        self.right_prev_button.clicked.connect(lambda: self.change_image('right', -1))
        self.right_next_button.clicked.connect(lambda: self.change_image('right', 1))

        # Image lists and indices
        self.left_images = []
        self.right_images = []
        self.left_index = 0
        self.right_index = 0

        self.data_frame = pd.DataFrame()

    def import_images(self, side):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder:
            images = sorted(glob.glob(os.path.join(folder, '*.png')),
                            key=lambda x: int(os.path.basename(x).replace('frame', '').replace('.png', '')))
            if side == 'left':
                self.left_images = images
                self.left_index = 0
                self.display_image('left')
                self.load_excel(folder)
                self.load_excel_data(self.data_frame)
            else:
                self.right_images = images
                self.right_index = 0
                self.display_image('right')

    def change_image(self, side, direction):
        if side == 'left' and self.left_images:
            self.left_index = (self.left_index + direction) % len(self.left_images)
            self.display_image('left')
            self.load_excel_data(self.data_frame)

        elif side == 'right' and self.right_images:
            self.right_index = (self.right_index + direction) % len(self.right_images)
            self.display_image('right')

    def display_image(self, side):
        if side == 'left' and self.left_images:
            pixmap = QPixmap(self.left_images[self.left_index])
            self.left_image_label.setPixmap(pixmap)
            self.left_filename_edit.setText(os.path.basename(self.left_images[self.left_index]).replace('.png', ''))
        elif side == 'right' and self.right_images:
            pixmap = QPixmap(self.right_images[self.right_index])
            self.right_image_label.setPixmap(pixmap)
            self.right_filename_edit.setText(os.path.basename(self.right_images[self.right_index]).replace('.png', ''))

    def load_excel(self, folder):
        excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
        if excel_files:
            df = pd.read_excel(excel_files[0])
            self.data_frame = df


    def load_excel_data(self, df):
        current_image_name = os.path.basename(self.left_images[self.left_index]).replace('frame', 'Frame')
        row = df[df['Frame'] == current_image_name]
        if not row.empty:
            headers = row.columns[row.iloc[0] == 1].tolist()
            self.left_text_edit.setText('\n'.join(headers))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())
