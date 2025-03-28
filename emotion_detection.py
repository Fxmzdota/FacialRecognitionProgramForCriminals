import tensorflow as tf
import cv2
import numpy as np
import database
from datetime import datetime

class EmotionDetector:
    def __init__(self):
        self.emotion_model = tf.keras.models.load_model("emotion_model.keras")
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_emotion(self, frame):
        """Detect emotion from a face in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return None, None
        
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (48, 48))
        face_roi = np.expand_dims(face_roi, axis=0)
        face_roi = np.expand_dims(face_roi, axis=-1)
        face_roi = face_roi.astype('float32') / 255.0
        
        emotion_prediction = self.emotion_model.predict(face_roi, verbose=0)
        emotion_index = np.argmax(emotion_prediction)
        predicted_emotion = self.emotion_labels[emotion_index]
        
        return predicted_emotion, (x, y, w, h)
    
    def analyze_emotion_trends(self, criminal_id):
        """Analyze emotion trends for a criminal and return conclusion"""
        logs = database.get_emotion_logs(criminal_id)
        if not logs:
            return "Insufficient Data", []
        
        emotions = [log[1] for log in logs]
        negative_emotions = ["Angry", "Disgust", "Fear", "Sad"]
        total = len(emotions)
        negative_count = sum(1 for emotion in emotions if emotion in negative_emotions)
        
        negative_ratio = negative_count / total
        if negative_ratio > 0.5:  # More than 50% negative emotions
            conclusion = "Confirmed suspect"
        else:
            conclusion = "Innocent civilian"
        
        timestamps = [log[0] for log in logs]
        emotion_sequence = [log[1] for log in logs]
        
        return conclusion, (timestamps, emotion_sequence)