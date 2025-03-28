import face_recognition
import dlib
import numpy as np
import cv2
import os
import csv
from datetime import datetime

# Initialize face detector
detector = dlib.get_frontal_face_detector()

class FaceRecognizer:
    def __init__(self, db_manager=None):  # Make db_manager optional
        self.known_criminals = {}  # name: encoding
        self.db_manager = db_manager
        self.load_criminals()
    
    def load_criminals(self):
        """Load known criminals from database"""
        try:
            if self.db_manager:  # If using database manager
                criminals = self.db_manager.get_all_criminals()
                for criminal in criminals:
                    if criminal[5]:  # if encoding exists
                        encoding = np.fromstring(criminal[5][1:-1], sep=',')
                        self.known_criminals[criminal[1]] = encoding
            else:  # Fallback to CSV
                with open("criminal_database.csv", "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        name, encoding_str = row[0], row[1]
                        encoding = np.fromstring(encoding_str[1:-1], sep=',')
                        self.known_criminals[name] = encoding
        except FileNotFoundError:
            print("No criminal database found. Starting fresh.")
    
    def recognize_faces(self, frame):
        """Detect and recognize faces in a frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        detected_names = []
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(list(self.known_criminals.values()), face_encoding)
            name = "Unknown"
            if True in matches:
                matched_idx = matches.index(True)
                name = list(self.known_criminals.keys())[matched_idx]
            detected_names.append(name)
        
        return detected_names, face_locations
    
    def capture_face_encoding(self, frame):
        """Capture and return face encoding from a frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_frame)
        if face_encodings:
            return face_encodings[0]
        return None