#!/usr/bin/env python3
"""
Face Recognition Module using FaceNet Embeddings
Recognize persons from stored embedding vectors
Raspberry Pi 5 Compatible
"""

import os
import cv2
import numpy as np
import json
import threading
from pathlib import Path
from utils import logger

try:
    import mediapipe as mp
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False
    logger.warning("MediaPipe not available")

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing import image
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available. Install with: pip install tensorflow")


class FaceRecognitionModule:
    """Face detection and recognition with embeddings"""
    
    def __init__(self, embedding_model_path=None, embeddings_db_path=None, confidence_threshold=0.6):
        """
        Initialize face recognition
        
        Args:
            embedding_model_path: Path to FaceNet model
            embeddings_db_path: Path to store/load embeddings JSON
            confidence_threshold: Similarity threshold for recognition
        """
        self.confidence_threshold = confidence_threshold
        self.embeddings_db_path = embeddings_db_path or "face_embeddings.json"
        self.lock = threading.Lock()
        
        # MediaPipe face detection
        self.face_detector = None
        if MP_AVAILABLE:
            try:
                # Try solutions API (works with mediapipe-rpi4)
                mp_face_detection = mp.solutions.face_detection
                self.face_detector = mp_face_detection.FaceDetection(
                    model_selection=0,
                    min_detection_confidence=0.7
                )
                logger.info("MediaPipe Solutions Face Detector initialized")
            except Exception as e:
                logger.warning(f"MediaPipe initialization failed: {e}")
                logger.info("Will use OpenCV Haar Cascade as fallback")
                self.face_detector = None
        else:
            logger.warning("MediaPipe not available - face detection disabled")
        
        # FaceNet model for embeddings
        self.embedding_model = None
        self.embeddings_db = {}
        
        try:
            logger.info("Initializing Face Recognition Module...")
            
            # Load embedding model (FaceNet)
            if embedding_model_path and os.path.exists(embedding_model_path):
                logger.info(f"Loading FaceNet model from {embedding_model_path}")
                if TENSORFLOW_AVAILABLE:
                    self.embedding_model = load_model(embedding_model_path)
                    logger.info("FaceNet model loaded")
            else:
                logger.warning(f"FaceNet model not found at {embedding_model_path}")
            
            # Load existing embeddings database
            self._load_embeddings_db()
            
            logger.info("Face Recognition Module initialized")
            
        except Exception as e:
            logger.error(f"Face Recognition initialization failed: {e}")
            raise
    
    def _load_embeddings_db(self):
        """Load embeddings from JSON file"""
        if os.path.exists(self.embeddings_db_path):
            try:
                with open(self.embeddings_db_path, 'r') as f:
                    self.embeddings_db = json.load(f)
                logger.info(f"Loaded {len(self.embeddings_db)} person embeddings")
            except Exception as e:
                logger.error(f"Failed to load embeddings database: {e}")
                self.embeddings_db = {}
        else:
            logger.info("No embeddings database found - starting fresh")
            self.embeddings_db = {}
    
    def _save_embeddings_db(self):
        """Save embeddings to JSON file"""
        try:
            with open(self.embeddings_db_path, 'w') as f:
                json.dump(self.embeddings_db, f, indent=2)
            logger.info(f"Saved {len(self.embeddings_db)} person embeddings")
        except Exception as e:
            logger.error(f"Failed to save embeddings database: {e}")
    
    def detect_faces(self, frame):
        """
        Detect faces in frame
        
        Args:
            frame: Input image frame
        
        Returns:
            List of face detections with bounding boxes
        """
        if frame is None:
            return []
        
        try:
            detections = []
            h, w = frame.shape[:2]
            
            # Try MediaPipe if available
            if self.face_detector is not None:
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Try solutions API (older but stable)
                    if hasattr(self.face_detector, 'process'):
                        results = self.face_detector.process(rgb_frame)
                        
                        if results and hasattr(results, 'detections') and results.detections:
                            for detection in results.detections:
                                bbox = detection.location_data.relative_bounding_box
                                
                                # Convert to pixel coordinates
                                x1 = max(0, int(bbox.xmin * w))
                                y1 = max(0, int(bbox.ymin * h))
                                x2 = min(w, int((bbox.xmin + bbox.width) * w))
                                y2 = min(h, int((bbox.ymin + bbox.height) * h))
                                
                                # Ensure valid box
                                if x2 > x1 and y2 > y1:
                                    detections.append({
                                        'bbox': (x1, y1, x2, y2),
                                        'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                                        'confidence': float(detection.score[0]) if detection.score else 0.8
                                    })
                        
                        if detections:
                            return detections
                except Exception as e:
                    logger.warning(f"MediaPipe detection failed: {e}, falling back to OpenCV")
            
            # Fallback: Use OpenCV Haar Cascade for face detection
            logger.debug("Using OpenCV Haar Cascade for face detection")
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            for (x, y, width, height) in faces:
                detections.append({
                    'bbox': (x, y, x + width, y + height),
                    'center': (x + width // 2, y + height // 2),
                    'confidence': 0.8
                })
            
            return detections
        
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []
    
    def extract_embedding(self, face_image):
        """
        Extract 128-d embedding from face
        
        Args:
            face_image: Cropped face image
        
        Returns:
            128-d embedding vector or None
        """
        if face_image is None or face_image.size == 0:
            return None

        try:
            # If FaceNet model is available, use it for high-quality embeddings
            if self.embedding_model is not None:
                face_resized = cv2.resize(face_image, (160, 160))
                face_normalized = face_resized.astype('float32') / 255.0
                x = np.expand_dims(face_normalized, axis=0)
                embedding = self.embedding_model.predict(x, verbose=0)
                embedding = embedding / (np.linalg.norm(embedding) + 1e-7)
                return embedding[0]

            # Fallback: compute a simple OpenCV-based embedding (histogram + edge stats)
            logger.debug("Embedding model not loaded, using OpenCV fallback embedding")
            gray_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            face_resized = cv2.resize(gray_face, (160, 160))

            # Basic statistical features
            mean = np.mean(face_resized)
            std = np.std(face_resized)

            # Histogram (16 bins)
            hist = cv2.calcHist([face_resized], [0], None, [16], [0, 256]).flatten()
            hist = hist / (hist.sum() + 1e-7)

            # Edge magnitude statistics
            sobelx = cv2.Sobel(face_resized, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(face_resized, cv2.CV_64F, 0, 1, ksize=3)
            edges_mean = np.mean(np.sqrt(sobelx**2 + sobely**2))

            embedding = np.concatenate([
                [mean, std, edges_mean],
                hist[:16],
                [np.mean(sobelx), np.mean(sobely)]
            ])
            embedding = embedding / (np.linalg.norm(embedding) + 1e-7)
            return embedding

        except Exception as e:
            logger.error(f"Embedding extraction error: {e}")
            return None
    
    def recognize_face(self, embedding):
        """
        Recognize face by comparing with stored embeddings
        
        Args:
            embedding: 128-d embedding vector
        
        Returns:
            Tuple (person_name, confidence) or (None, 0.0) if not recognized
        """
        if embedding is None or len(self.embeddings_db) == 0:
            return None, 0.0
        
        try:
            best_match = None
            best_distance = float('inf')
            
            # Compare with all stored embeddings
            for person_name, stored_embeddings_list in self.embeddings_db.items():
                for stored_embedding in stored_embeddings_list:
                    # Calculate Euclidean distance
                    stored_vec = np.array(stored_embedding)
                    distance = np.linalg.norm(embedding - stored_vec)
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_match = person_name
            
            # Convert distance to confidence (lower distance = higher confidence)
            # Threshold typically around 0.6-1.0 for Euclidean distance
            confidence = 1.0 / (1.0 + best_distance) if best_distance < 2.0 else 0.0
            
            if confidence >= self.confidence_threshold:
                logger.info(f"Face recognized: {best_match} (confidence: {confidence:.2f})")
                return best_match, confidence
            else:
                logger.info(f"Unknown face (best match: {best_match} with confidence {confidence:.2f})")
                return None, confidence
        
        except Exception as e:
            logger.error(f"Face recognition error: {e}")
            return None, 0.0
    
    def add_embedding(self, person_name, embedding):
        """
        Add embedding to database
        
        Args:
            person_name: Name of person
            embedding: 128-d embedding vector
        """
        try:
            embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            if person_name not in self.embeddings_db:
                self.embeddings_db[person_name] = []
            
            self.embeddings_db[person_name].append(embedding_list)
            self._save_embeddings_db()
            
            logger.info(f"Added embedding for {person_name}")
        
        except Exception as e:
            logger.error(f"Failed to add embedding: {e}")
    
    def process_faces_from_folder(self, folder_path, person_name):
        """
        Process images from folder and create embeddings
        
        Args:
            folder_path: Path to folder with face images
            person_name: Name of person
        
        Returns:
            Number of successful embeddings
        """
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return 0
        
        try:
            count = 0
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
            
            for filename in os.listdir(folder_path):
                if os.path.splitext(filename)[1].lower() not in image_extensions:
                    continue
                
                image_path = os.path.join(folder_path, filename)
                
                try:
                    # Read image
                    img = cv2.imread(image_path)
                    if img is None:
                        continue
                    
                    # Detect faces
                    faces = self.detect_faces(img)
                    
                    for face in faces:
                        x1, y1, x2, y2 = face['bbox']
                        face_crop = img[y1:y2, x1:x2]
                        
                        # Extract embedding
                        embedding = self.extract_embedding(face_crop)
                        
                        if embedding is not None:
                            # Add to database
                            self.add_embedding(person_name, embedding)
                            count += 1
                            logger.info(f"Processed {filename} - embedding #{count}")
                
                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")
                    continue
            
            logger.info(f"Processed {count} embeddings for {person_name}")
            return count
        
        except Exception as e:
            logger.error(f"Folder processing error: {e}")
            return 0
    
    def get_person_count(self):
        """Get number of recognized people"""
        return len(self.embeddings_db)
    
    def get_people_list(self):
        """Get list of recognized people"""
        return list(self.embeddings_db.keys())
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Face Recognition Module")
        if self.face_detector:
            try:
                self.face_detector.close()
            except:
                pass
        logger.info("Face Recognition cleanup complete")
    
    def _load_embeddings_db(self):
        """Load embeddings from JSON file"""
        if os.path.exists(self.embeddings_db_path):
            try:
                with open(self.embeddings_db_path, 'r') as f:
                    self.embeddings_db = json.load(f)
                logger.info(f"Loaded {len(self.embeddings_db)} person embeddings")
            except Exception as e:
                logger.error(f"Failed to load embeddings database: {e}")
                self.embeddings_db = {}
        else:
            logger.info("No embeddings database found - starting fresh")
            self.embeddings_db = {}
    
    def _save_embeddings_db(self):
        """Save embeddings to JSON file"""
        try:
            with open(self.embeddings_db_path, 'w') as f:
                json.dump(self.embeddings_db, f, indent=2)
            logger.info(f"Saved {len(self.embeddings_db)} person embeddings")
        except Exception as e:
            logger.error(f"Failed to save embeddings database: {e}")

    
    def extract_embedding(self, face_image):
        """
        Extract 128-d embedding from face
        
        Args:
            face_image: Cropped face image
        
        Returns:
            128-d embedding vector or None
        """
        if self.embedding_model is None:
            logger.warning("Embedding model not loaded")
            return None
        
        if face_image is None or face_image.size == 0:
            return None
        
        try:
            # Resize to model input size (160x160 for FaceNet)
            face_resized = cv2.resize(face_image, (160, 160))
            face_normalized = face_resized.astype('float32') / 255.0
            
            # Add batch dimension
            x = np.expand_dims(face_normalized, axis=0)
            
            # Get embedding
            embedding = self.embedding_model.predict(x, verbose=0)
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding[0]
        
        except Exception as e:
            logger.error(f"Embedding extraction error: {e}")
            return None
    
    def recognize_face(self, embedding):
        """
        Recognize face by comparing with stored embeddings
        
        Args:
            embedding: 128-d embedding vector
        
        Returns:
            Tuple (person_name, confidence) or (None, 0.0) if not recognized
        """
        if embedding is None or len(self.embeddings_db) == 0:
            return None, 0.0
        
        try:
            best_match = None
            best_distance = float('inf')
            
            # Compare with all stored embeddings
            for person_name, stored_embeddings_list in self.embeddings_db.items():
                for stored_embedding in stored_embeddings_list:
                    # Calculate Euclidean distance
                    stored_vec = np.array(stored_embedding)
                    distance = np.linalg.norm(embedding - stored_vec)
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_match = person_name
            
            # Convert distance to confidence (lower distance = higher confidence)
            # Threshold typically around 0.6-1.0 for Euclidean distance
            confidence = 1.0 / (1.0 + best_distance) if best_distance < 2.0 else 0.0
            
            if confidence >= self.confidence_threshold:
                logger.info(f"Face recognized: {best_match} (confidence: {confidence:.2f})")
                return best_match, confidence
            else:
                logger.info(f"Unknown face (best match: {best_match} with confidence {confidence:.2f})")
                return None, confidence
        
        except Exception as e:
            logger.error(f"Face recognition error: {e}")
            return None, 0.0
    
    def add_embedding(self, person_name, embedding):
        """
        Add embedding to database
        
        Args:
            person_name: Name of person
            embedding: 128-d embedding vector
        """
        try:
            embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            if person_name not in self.embeddings_db:
                self.embeddings_db[person_name] = []
            
            self.embeddings_db[person_name].append(embedding_list)
            self._save_embeddings_db()
            
            logger.info(f"Added embedding for {person_name}")
        
        except Exception as e:
            logger.error(f"Failed to add embedding: {e}")
    
    def process_faces_from_folder(self, folder_path, person_name):
        """
        Process images from folder and create embeddings
        
        Args:
            folder_path: Path to folder with face images
            person_name: Name of person
        
        Returns:
            Number of successful embeddings
        """
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return 0
        
        try:
            count = 0
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
            
            for filename in os.listdir(folder_path):
                if os.path.splitext(filename)[1].lower() not in image_extensions:
                    continue
                
                image_path = os.path.join(folder_path, filename)
                
                try:
                    # Read image
                    img = cv2.imread(image_path)
                    if img is None:
                        continue
                    
                    # Detect faces
                    faces = self.detect_faces(img)
                    
                    for face in faces:
                        x1, y1, x2, y2 = face['bbox']
                        face_crop = img[y1:y2, x1:x2]
                        
                        # Extract embedding
                        embedding = self.extract_embedding(face_crop)
                        
                        if embedding is not None:
                            # Add to database
                            self.add_embedding(person_name, embedding)
                            count += 1
                            logger.info(f"Processed {filename} - embedding #{count}")
                
                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")
                    continue
            
            logger.info(f"Processed {count} embeddings for {person_name}")
            return count
        
        except Exception as e:
            logger.error(f"Folder processing error: {e}")
            return 0
    
    def get_person_count(self):
        """Get number of recognized people"""
        return len(self.embeddings_db)
    
    def get_people_list(self):
        """Get list of recognized people"""
        return list(self.embeddings_db.keys())
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Face Recognition Module")
        if self.face_detector:
            self.face_detector.close()
        logger.info("Face Recognition cleanup complete")
