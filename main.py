
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QListWidget, QPushButton, QFileDialog, QLabel, QMessageBox,
                            QScrollArea, QSplitter, QFrame, QSlider, QMenu, QAction)
from PyQt5.QtGui import QIcon, QCursor, QPainter, QColor, QPen, QLinearGradient
from PyQt5.QtCore import Qt, QRect, QPoint, QSize

from audio_processor import AudioProcessor
from waveform_viewer import WaveformViewer
from timeline import Timeline

class AudioEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_processor = AudioProcessor()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Audio Timeline Weaver")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2D2D2D;
                color: #ECECEC;
            }
            QPushButton {
                background-color: #444444;
                border: none;
                color: #ECECEC;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #666666;
            }
            QListWidget {
                background-color: #3D3D3D;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                color: #ECECEC;
            }
            QLabel {
                color: #ECECEC;
            }
            QSlider {
                background-color: transparent;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #555555;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #ECECEC;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Top controls
        top_controls = QWidget()
        top_layout = QHBoxLayout(top_controls)

        # Import button
        import_btn = QPushButton("Import Audio")
        import_btn.clicked.connect(self.import_audio)
        top_layout.addWidget(import_btn)

        # Export button
        export_btn = QPushButton("Export Audio")
        export_btn.clicked.connect(self.export_audio)
        top_layout.addWidget(export_btn)

        # Add some space
        top_layout.addStretch()

        # Playback controls
        play_btn = QPushButton("Play")
        play_btn.clicked.connect(self.play_audio)
        top_layout.addWidget(play_btn)
        
        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.stop_audio)
        top_layout.addWidget(stop_btn)
        
        main_layout.addWidget(top_controls)

        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Library
        library_panel = QWidget()
        library_layout = QVBoxLayout(library_panel)
        library_label = QLabel("Audio Library")
        library_layout.addWidget(library_label)
        
        self.file_list = QListWidget()
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_library_context_menu)
        self.file_list.itemDoubleClicked.connect(self.add_to_timeline)
        library_layout.addWidget(self.file_list)
        
        splitter.addWidget(library_panel)

        # Right panel - Timeline and waveform
        timeline_panel = QWidget()
        timeline_layout = QVBoxLayout(timeline_panel)
        
        # Waveform viewer
        self.waveform_viewer = WaveformViewer(self)
        timeline_layout.addWidget(self.waveform_viewer)
        
        # Timeline
        self.timeline = Timeline(self)
        timeline_layout.addWidget(self.timeline)
        
        # Timeline tools
        tools_layout = QHBoxLayout()
        
        cut_btn = QPushButton("Cut")
        cut_btn.clicked.connect(self.cut_audio)
        tools_layout.addWidget(cut_btn)
        
        split_btn = QPushButton("Split")
        split_btn.clicked.connect(self.split_audio)
        tools_layout.addWidget(split_btn)
        
        delete_btn = QPushButton("Delete Selection")
        delete_btn.clicked.connect(self.delete_selection)
        tools_layout.addWidget(delete_btn)
        
        timeline_layout.addLayout(tools_layout)
        
        splitter.addWidget(timeline_panel)
        
        # Set initial sizes
        splitter.setSizes([300, 900])
        main_layout.addWidget(splitter)

        # Status bar for feedback
        self.statusBar().showMessage("Ready")

    def import_audio(self):
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Import Audio Files", "", 
            "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)", 
            options=options
        )
        
        if file_paths:
            for file_path in file_paths:
                try:
                    file_name = os.path.basename(file_path)
                    self.audio_processor.load_file(file_path)
                    self.file_list.addItem(file_name)
                    self.statusBar().showMessage(f"Imported: {file_name}")
                except Exception as e:
                    QMessageBox.critical(self, "Import Error", 
                                       f"Failed to import {file_path}: {str(e)}")
    
    def show_library_context_menu(self, position):
        if self.file_list.count() > 0:
            menu = QMenu()
            add_to_timeline = QAction("Add to Timeline", self)
            remove_from_library = QAction("Remove from Library", self)
            
            menu.addAction(add_to_timeline)
            menu.addAction(remove_from_library)
            
            add_to_timeline.triggered.connect(self.add_selected_to_timeline)
            remove_from_library.triggered.connect(self.remove_from_library)
            
            menu.exec_(QCursor.pos())
    
    def add_selected_to_timeline(self):
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            self.add_to_timeline(item)
    
    def add_to_timeline(self, item):
        file_name = item.text()
        audio_data = self.audio_processor.get_audio_data(file_name)
        if audio_data:
            self.timeline.add_audio_clip(file_name, audio_data)
            self.statusBar().showMessage(f"Added {file_name} to timeline")
    
    def remove_from_library(self):
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            row = self.file_list.row(item)
            file_name = item.text()
            self.file_list.takeItem(row)
            self.audio_processor.remove_file(file_name)
            self.statusBar().showMessage(f"Removed {file_name} from library")
    
    def play_audio(self):
        self.statusBar().showMessage("Playing audio...")
        # In a real implementation, we would connect to audio playback
        # For this demo, we'll just update the status
    
    def stop_audio(self):
        self.statusBar().showMessage("Playback stopped")
        # In a real implementation, we would stop audio playback
    
    def cut_audio(self):
        self.statusBar().showMessage("Cut operation not implemented in this demo")
        # In a real implementation, we would cut the selected audio
    
    def split_audio(self):
        self.statusBar().showMessage("Split operation not implemented in this demo")
        # In a real implementation, we would split the audio at the current position
    
    def delete_selection(self):
        self.statusBar().showMessage("Delete operation not implemented in this demo")
        # In a real implementation, we would delete the selected audio region
    
    def export_audio(self):
        options = QFileDialog.Options()
        file_path, file_type = QFileDialog.getSaveFileName(
            self, "Export Audio", "", 
            "MP3 Files (*.mp3);;WAV Files (*.wav)", 
            options=options
        )
        
        if file_path:
            try:
                # In a real implementation, we would export the timeline audio
                self.statusBar().showMessage(f"Audio exported to {file_path}")
                QMessageBox.information(self, "Export Successful", 
                                      f"Audio successfully exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", 
                                   f"Failed to export audio: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = AudioEditor()
    editor.show()
    sys.exit(app.exec_())
