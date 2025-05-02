
from PyQt5.QtWidgets import QWidget, QScrollArea, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient
from PyQt5.QtCore import Qt, QRect, QPoint, QSize

class AudioClip(QWidget):
    def __init__(self, file_name, audio_data, parent=None):
        super().__init__(parent)
        self.file_name = file_name
        self.audio_data = audio_data
        self.setFixedHeight(80)
        self.setMinimumWidth(int(audio_data['duration'] * 100))  # 100 pixels per second
        self.samples = audio_data['samples']
        self.duration = audio_data['duration']
        self.setStyleSheet("background-color: #444444; border-radius: 4px;")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw clip background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor('#555555'))
        gradient.setColorAt(1, QColor('#444444'))
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # Draw borders
        painter.setPen(QPen(QColor('#666666'), 1))
        painter.drawRoundedRect(0, 0, self.width()-1, self.height()-1, 4, 4)
        
        # Draw clip name
        painter.setPen(Qt.white)
        painter.drawText(10, 20, self.file_name)
        
        # Draw waveform preview
        if self.samples is not None and len(self.samples) > 0:
            painter.setPen(QPen(QColor('#00AAFF'), 1))
            center_y = self.height() / 2 + 10
            
            # Calculate step to fit the waveform in the clip width
            step = max(1, len(self.samples) // self.width())
            
            for i in range(0, self.width()):
                # Calculate sample index
                index = i * step
                if index >= len(self.samples):
                    break
                    
                # Get sample value (-1 to 1)
                value = self.samples[index]
                
                # Scale to widget height
                amplitude = value * self.height() * 0.3  # 30% of widget height
                
                # Draw vertical line from center
                x = i
                y1 = int(center_y - amplitude)
                y2 = int(center_y + amplitude)
                
                painter.drawLine(x, y1, x, y2)

class Timeline(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumHeight(200)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setStyleSheet("background-color: #333333; border: 1px solid #555555;")
        
        # Container widget
        self.container = QWidget()
        self.setWidget(self.container)
        
        # Container layout
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Timeline tracks
        self.tracks = []
        self.add_track()
    
    def add_track(self):
        """Add a new track to the timeline"""
        track = QWidget()
        track_layout = QHBoxLayout(track)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(5)
        track_layout.addStretch()
        
        self.tracks.append({
            'widget': track,
            'layout': track_layout,
            'clips': []
        })
        
        self.layout.addWidget(track)
    
    def add_audio_clip(self, file_name, audio_data, track_index=0):
        """Add an audio clip to the timeline"""
        # Make sure we have enough tracks
        while track_index >= len(self.tracks):
            self.add_track()
        
        # Create audio clip widget
        clip = AudioClip(file_name, audio_data)
        
        # Add to track
        track = self.tracks[track_index]
        
        # Remove stretch before adding clips
        if track['layout'].count() > 0:
            stretch_item = track['layout'].itemAt(track['layout'].count() - 1)
            if stretch_item:
                track['layout'].removeItem(stretch_item)
        
        # Add the clip
        track['layout'].addWidget(clip)
        track['clips'].append(clip)
        
        # Add stretch at the end
        track['layout'].addStretch()
        
        # Update the parent's waveform viewer
        if hasattr(self.parent, 'waveform_viewer'):
            self.parent.waveform_viewer.set_waveform_data(audio_data['samples'])
        
        return clip
    
    def clear_timeline(self):
        """Remove all clips from the timeline"""
        for track in self.tracks:
            for clip in track['clips']:
                track['layout'].removeWidget(clip)
                clip.deleteLater()
            track['clips'] = []
