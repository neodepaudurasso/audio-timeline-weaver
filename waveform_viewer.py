
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QLinearGradient
from PyQt5.QtCore import Qt, QRect
import numpy as np

class WaveformViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.waveform_data = None
        self.start_position = 0
        self.zoom_level = 1.0
        self.selection_start = None
        self.selection_end = None
        self.setStyleSheet("background-color: #2A2A2A; border: 1px solid #444444;")
    
    def set_waveform_data(self, data):
        """Set the waveform data to display"""
        self.waveform_data = data
        self.update()
    
    def set_selection(self, start, end):
        """Set the selected region"""
        self.selection_start = start
        self.selection_end = end
        self.update()
    
    def clear_selection(self):
        """Clear the selected region"""
        self.selection_start = None
        self.selection_end = None
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor('#2A2A2A'))
        
        if self.waveform_data is None:
            # Draw placeholder text if no data
            painter.setPen(QColor('#666666'))
            painter.drawText(self.rect(), Qt.AlignCenter, "No audio loaded")
            return
        
        # Draw selection region if exists
        if self.selection_start is not None and self.selection_end is not None:
            start_x = self.selection_start * self.width()
            end_x = self.selection_end * self.width()
            selection_rect = QRect(int(start_x), 0, int(end_x - start_x), self.height())
            selection_color = QColor(0, 120, 215, 100)  # Semi-transparent blue
            painter.fillRect(selection_rect, selection_color)
        
        # Draw waveform
        painter.setPen(QPen(QColor('#00AAFF'), 1))
        
        center_y = self.height() / 2
        samples = self.waveform_data
        
        # Calculate visible samples based on zoom and position
        visible_start = int(self.start_position * len(samples))
        visible_samples = int(len(samples) / self.zoom_level)
        visible_end = min(visible_start + visible_samples, len(samples))
        
        if visible_end <= visible_start:
            return
        
        # Get visible samples
        visible_data = samples[visible_start:visible_end]
        
        # Calculate step to fit the waveform in the widget width
        step = max(1, len(visible_data) // self.width())
        
        # Draw waveform lines
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 170, 255))
        gradient.setColorAt(1, QColor(0, 100, 150))
        painter.setBrush(gradient)
        
        for i in range(0, self.width()):
            # Calculate sample index
            index = int(i * step * self.zoom_level)
            if index >= len(visible_data):
                break
                
            # Get sample value (-1 to 1)
            value = visible_data[index]
            
            # Scale to widget height
            amplitude = value * self.height() * 0.4  # 40% of widget height
            
            # Draw vertical line from center
            x = i
            y1 = int(center_y - amplitude)
            y2 = int(center_y + amplitude)
            
            painter.drawLine(x, y1, x, y2)
        
        # Draw center line
        painter.setPen(QPen(QColor('#444444'), 1))
        painter.drawLine(0, int(center_y), self.width(), int(center_y))
        
        # Draw time markers
        # In a real implementation, we would draw time markers along the bottom
