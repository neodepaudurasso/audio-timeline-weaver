
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QListWidget, QPushButton, QFileDialog, QLabel, QMessageBox,
                            QScrollArea, QSplitter, QFrame, QSlider, QMenu, QAction)
from PyQt5.QtGui import QIcon, QCursor, QPainter, QColor, QPen, QLinearGradient
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QTimer

from audio_processor import AudioProcessor
from waveform_viewer import WaveformViewer
from timeline import Timeline

class AudioEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_processor = AudioProcessor()
        self.current_file = None
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.update_playhead)
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
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_audio)
        top_layout.addWidget(self.play_btn)
        
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
        self.timeline.clip_clicked.connect(self.on_clip_clicked)
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
        
        # Position slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setMinimum(0)
        self.position_slider.setMaximum(1000)
        self.position_slider.setValue(0)
        self.position_slider.setTracking(True)
        self.position_slider.valueChanged.connect(self.on_slider_value_changed)
        timeline_layout.addWidget(self.position_slider)
        
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
                    success = self.audio_processor.load_file(file_path)
                    if success:
                        self.file_list.addItem(file_name)
                        self.statusBar().showMessage(f"Imported: {file_name}")
                    else:
                        QMessageBox.warning(self, "Import Warning", 
                            f"Failed to import {file_name}. Check if FFmpeg is properly configured.")
                except Exception as e:
                    QMessageBox.critical(self, "Import Error", 
                                       f"Failed to import {file_path}: {str(e)}")
    
    def show_library_context_menu(self, position):
        if self.file_list.count() > 0:
            menu = QMenu()
            add_to_timeline = QAction("Add to Timeline", self)
            remove_from_library = QAction("Remove from Library", self)
            play_audio = QAction("Play", self)
            
            menu.addAction(add_to_timeline)
            menu.addAction(play_audio)
            menu.addAction(remove_from_library)
            
            add_to_timeline.triggered.connect(self.add_selected_to_timeline)
            play_audio.triggered.connect(self.play_selected_audio)
            remove_from_library.triggered.connect(self.remove_from_library)
            
            menu.exec_(QCursor.pos())
    
    def add_selected_to_timeline(self):
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            self.add_to_timeline(item)
    
    def play_selected_audio(self):
        selected_items = self.file_list.selectedItems()
        if selected_items:
            file_name = selected_items[0].text()
            self.play_specific_audio(file_name)
    
    def play_specific_audio(self, file_name):
        """Play a specific audio file"""
        if self.audio_processor.play_audio(file_name):
            self.current_file = file_name
            self.play_btn.setText("Pause")
            self.statusBar().showMessage(f"Playing: {file_name}")
            
            # Start the playback timer to update the playhead
            self.playback_timer.start(100)  # Update every 100ms
        else:
            self.statusBar().showMessage(f"Failed to play: {file_name}")
    
    def add_to_timeline(self, item):
        file_name = item.text()
        audio_data = self.audio_processor.get_audio_data(file_name)
        if audio_data:
            self.timeline.add_audio_clip(file_name, audio_data)
            self.statusBar().showMessage(f"Added {file_name} to timeline")
            # If this is the first clip, set it as the current file
            if self.current_file is None:
                self.current_file = file_name
    
    def on_clip_clicked(self, file_name):
        """Handle clip click in timeline"""
        self.current_file = file_name
        self.statusBar().showMessage(f"Selected: {file_name}")
        
        # Update waveform viewer
        audio_data = self.audio_processor.get_audio_data(file_name)
        if audio_data:
            self.waveform_viewer.set_waveform_data(audio_data['samples'])
    
    def remove_from_library(self):
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            row = self.file_list.row(item)
            file_name = item.text()
            self.file_list.takeItem(row)
            self.audio_processor.remove_file(file_name)
            self.statusBar().showMessage(f"Removed {file_name} from library")
    
    def play_audio(self):
        """Play or pause audio"""
        if self.current_file:
            if not self.audio_processor.is_playing:
                self.play_specific_audio(self.current_file)
            else:
                self.pause_audio()
        else:
            self.statusBar().showMessage("No audio selected to play")
    
    def pause_audio(self):
        """Pause audio playback"""
        # In a real implementation, we would pause the audio
        # For pygame, we can just stop it for now
        self.audio_processor.stop_audio()
        self.play_btn.setText("Play")
        self.playback_timer.stop()
        self.statusBar().showMessage("Playback paused")
    
    def stop_audio(self):
        """Stop audio playback"""
        self.audio_processor.stop_audio()
        self.play_btn.setText("Play")
        self.playback_timer.stop()
        self.position_slider.setValue(0)
        self.waveform_viewer.set_playhead_position(0)
        self.statusBar().showMessage("Playback stopped")
    
    def update_playhead(self):
        """Update the playhead position during playback"""
        if pygame.mixer.music.get_busy():
            # Get current position (this is approximate in pygame)
            try:
                pos = pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds
                audio_data = self.audio_processor.get_audio_data(self.current_file)
                if audio_data:
                    duration = audio_data['duration']
                    if duration > 0:
                        relative_pos = pos / duration
                        self.position_slider.setValue(int(relative_pos * 1000))
                        self.waveform_viewer.set_playhead_position(relative_pos)
            except:
                pass
        else:
            # Playback finished
            self.stop_audio()
    
    def on_slider_value_changed(self, value):
        """Handle position slider value change"""
        position = value / 1000.0  # Convert to 0.0-1.0 range
        self.waveform_viewer.set_playhead_position(position)
        
        # In a full implementation, we would seek the audio to this position
        # This is complex to do with pygame, so we won't implement it here
    
    def on_playhead_moved(self, position):
        """Handle playhead movement from waveform viewer"""
        self.position_slider.setValue(int(position * 1000))
    
    def cut_audio(self):
        if self.current_file and self.waveform_viewer.selection_start is not None and self.waveform_viewer.selection_end is not None:
            # Get audio data
            audio_data = self.audio_processor.get_audio_data(self.current_file)
            if not audio_data:
                self.statusBar().showMessage("No audio data available")
                return
            
            # Calculate times based on selection and duration
            start_time = self.waveform_viewer.selection_start * audio_data['duration']
            end_time = self.waveform_viewer.selection_end * audio_data['duration']
            
            # Cut the audio
            new_file_name = self.audio_processor.cut_audio(self.current_file, start_time, end_time)
            if new_file_name:
                self.file_list.addItem(new_file_name)
                self.statusBar().showMessage(f"Created: {new_file_name}")
                
                # Clear selection
                self.waveform_viewer.clear_selection()
            else:
                self.statusBar().showMessage("Failed to cut audio")
        else:
            self.statusBar().showMessage("Please select a region to cut")
    
    def split_audio(self):
        if self.current_file:
            # Get playhead position
            playhead_pos = self.waveform_viewer.playhead_position
            
            # Get audio data
            audio_data = self.audio_processor.get_audio_data(self.current_file)
            if not audio_data:
                self.statusBar().showMessage("No audio data available")
                return
            
            # Calculate split time
            split_time = playhead_pos * audio_data['duration']
            
            # Split the audio
            result = self.audio_processor.split_audio(self.current_file, split_time)
            if result:
                first_file, second_file = result
                self.file_list.addItem(first_file)
                self.file_list.addItem(second_file)
                self.statusBar().showMessage(f"Split into: {first_file} and {second_file}")
            else:
                self.statusBar().showMessage("Failed to split audio")
        else:
            self.statusBar().showMessage("No audio selected for splitting")
    
    def delete_selection(self):
        self.statusBar().showMessage("Delete operation not implemented in this demo")
        # In a real implementation, we would delete the selected audio region
        self.waveform_viewer.clear_selection()
    
    def export_audio(self):
        options = QFileDialog.Options()
        file_path, file_type = QFileDialog.getSaveFileName(
            self, "Export Audio", "", 
            "MP3 Files (*.mp3);;WAV Files (*.wav)", 
            options=options
        )
        
        if file_path:
            try:
                # Collect all clips from the timeline
                timeline_clips = []
                for track in self.timeline.tracks:
                    for clip_widget in track['clips']:
                        timeline_clips.append({
                            'file_name': clip_widget.file_name,
                            'start_time': 0  # In a full implementation, we'd track actual start times
                        })
                
                # Export the audio
                success, message = self.audio_processor.export_audio(file_path, timeline_clips)
                
                if success:
                    self.statusBar().showMessage(f"Audio exported to {file_path}")
                    QMessageBox.information(self, "Export Successful", message)
                else:
                    QMessageBox.critical(self, "Export Error", message)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", 
                                   f"Failed to export audio: {str(e)}")

# Make sure pygame is available in the main module
import pygame

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = AudioEditor()
    editor.show()
    sys.exit(app.exec_())
