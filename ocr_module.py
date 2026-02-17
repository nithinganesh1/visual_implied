#!/usr/bin/env python3
"""
OCR Module for Text Recognition
Extracts text from image frames using EasyOCR
"""

import cv2
import numpy as np
from utils import logger

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not available. Install with: pip install easyocr")


class OCRModule:
    """Handles Optical Character Recognition on image frames"""
    
    def __init__(self, languages=['en', 'hi'], gpu=False):
        """
        Initialize OCR module
        
        Args:
            languages: List of languages to recognize (en=English, hi=Hindi)
            gpu: Whether to use GPU (if available)
        """
        self.languages = languages
        self.reader = None
        self.gpu = gpu
        
        if EASYOCR_AVAILABLE:
            try:
                logger.info(f"Initializing EasyOCR with languages: {languages}, GPU: {gpu}")
                self.reader = easyocr.Reader(languages, gpu=gpu)
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                self.reader = None
        else:
            logger.error("EasyOCR not available")
    
    def extract_text(self, frame, confidence_threshold=0.3):
        """
        Extract text from image frame
        
        Args:
            frame: Image frame (numpy array)
            confidence_threshold: Minimum confidence for text detection
        
        Returns:
            Tuple (extracted_text: str, detections: list, annotated_frame: numpy array)
        """
        if self.reader is None:
            logger.error("OCR reader not initialized")
            return "", [], frame
        
        if frame is None:
            logger.error("Frame is None")
            return "", [], frame
        
        try:
            # Perform OCR
            logger.debug("Performing OCR on frame...")
            results = self.reader.readtext(frame)
            
            # Extract text and filter by confidence
            text_lines = []
            detections = []
            
            for detection in results:
                bbox, text, confidence = detection
                
                if confidence >= confidence_threshold:
                    text_lines.append(text)
                    detections.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox
                    })
                    logger.debug(f"Detected text: '{text}' (confidence: {confidence:.2f})")
            
            # Combine text
            extracted_text = " ".join(text_lines)
            
            # Create annotated frame
            annotated_frame = self._annotate_frame(frame.copy(), detections)
            
            logger.info(f"OCR completed. Extracted text: {extracted_text[:100]}")
            
            return extracted_text, detections, annotated_frame
        
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return "", [], frame
    
    def _annotate_frame(self, frame, detections):
        """
        Draw bounding boxes and text on frame
        
        Args:
            frame: Image frame
            detections: List of text detections
        
        Returns:
            Annotated frame
        """
        for detection in detections:
            bbox = detection['bbox']
            text = detection['text']
            confidence = detection['confidence']
            
            # Convert bbox to integer coordinates
            pts = np.array(bbox, dtype=np.int32)
            
            # Draw bounding box
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            
            # Draw text label
            label = f"{text} ({confidence:.2f})"
            cv2.putText(
                frame,
                label,
                tuple(pts[0]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
        
        return frame
    
    def cleanup(self):
        """Cleanup OCR module"""
        logger.info("Cleaning up OCR module")
        self.reader = None
