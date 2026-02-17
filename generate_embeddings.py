#!/usr/bin/env python3
"""
Face Embedding Generator
Process images from 'georgy' folder to create embeddings database
Run once to generate face_embeddings.json, then delete folder
"""

import os
import sys
import shutil
from pathlib import Path
from face_recognition import FaceRecognitionModule
from utils import logger


def generate_embeddings_from_folder(georgy_folder, model_path=None):
    """
    Generate embeddings from georgy folder and save to JSON
    
    Args:
        georgy_folder: Path to georgy folder with images
        model_path: Path to FaceNet model
    
    Returns:
        Success/failure status
    """
    
    if not os.path.exists(georgy_folder):
        print(f"❌ Folder not found: {georgy_folder}")
        print(f"   Please create: mkdir {georgy_folder}")
        print(f"   Then add face images (jpg, png, bmp)")
        return False
    
    print(f"\n{'='*60}")
    print("FACE EMBEDDING GENERATOR")
    print(f"{'='*60}\n")
    
    print(f"📁 Source folder: {georgy_folder}")
    
    # Check if folder has images
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    images_found = []
    
    for item in os.listdir(georgy_folder):
        item_path = os.path.join(georgy_folder, item)
        if os.path.isfile(item_path) and os.path.splitext(item)[1].lower() in image_extensions:
            images_found.append(item)
    
    if not images_found:
        print(f"❌ No valid images found in {georgy_folder}")
        print(f"   Supported formats: jpg, jpeg, png, bmp")
        print(f"   Please add clear, frontal face photos")
        return False
    
    print(f"📷 Found {len(images_found)} image(s)")
    
    try:
        # Initialize face recognition module
        print("🔄 Initializing Face Recognition Module...")
        face_rec = FaceRecognitionModule(
            embedding_model_path=model_path,
            embeddings_db_path="face_embeddings.json",
            confidence_threshold=0.6
        )
        
        # Check if face detector is available
        if face_rec.face_detector is None:
            print("⚠️  Warning: Face detector not available")
            print("   Trying to continue anyway...")
        
        # Process images
        print(f"🔍 Processing {len(images_found)} images...")
        
        # If direct images (not in subfolders), use folder name as person
        count = 0
        
        # Try direct images first
        for img_file in images_found[:5]:  # Process first 5 as test
            print(f"  ✓ {img_file}")
        
        # Now process all with folder name as person
        print(f"\n📷 Processing images for 'georgy'...")
        count = face_rec.process_faces_from_folder(georgy_folder, "georgy")
        
        if count > 0:
            print(f"\n✅ Successfully processed {count} face embeddings!")
            print(f"💾 Embeddings saved to: face_embeddings.json\n")
            
            # Show summary
            people = face_rec.get_people_list()
            print(f"📊 Recognized people: {', '.join(people)}")
            print(f"👥 Total persons: {face_rec.get_person_count()}\n")
            
            return True
        else:
            print(f"\n❌ No faces detected in {georgy_folder}")
            print(f"   Make sure:")
            print(f"   ✓ Images have clear, visible faces")
            print(f"   ✓ Face is frontal or slightly angled")
            print(f"   ✓ Good lighting")
            print(f"   ✓ Image resolution at least 100x100 pixels")
            return False
    
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_folder(folder_path, keep_embeddings=True):
    """
    Delete georgy folder after embeddings are generated
    
    Args:
        folder_path: Path to folder to delete
        keep_embeddings: Keep face_embeddings.json file
    """
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"🗑️  Deleted: {folder_path}")
            
            if keep_embeddings and os.path.exists("face_embeddings.json"):
                print(f"✅ Kept embeddings file: face_embeddings.json")
            
            return True
        except Exception as e:
            print(f"❌ Failed to delete folder: {e}")
            return False
    
    return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SETUP: Generate Face Embeddings")
    print("="*60)
    
    georgy_folder = "/home/nithin/Evolve/projects/visual_implied/georgy"
    embeddings_file = "face_embeddings.json"
    
    # Check if folder exists
    if not os.path.exists(georgy_folder):
        print(f"\n⚠️  Folder does not exist: {georgy_folder}")
        print(f"   Creating folder...")
        os.makedirs(georgy_folder, exist_ok=True)
        print(f"✅ Created: {georgy_folder}")
        print(f"\n📝 Please add face images to: {georgy_folder}")
        print(f"   Then run this script again")
        sys.exit(0)
    
    # Check if embeddings already exist
    if os.path.exists(embeddings_file):
        print(f"\n⚠️  Embeddings file already exists: {embeddings_file}")
        response = input("Regenerate embeddings? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping regeneration.")
            sys.exit(0)
    
    # Generate embeddings
    success = generate_embeddings_from_folder(georgy_folder)
    
    if success:
        # Ask to cleanup folder
        response = input("\n🗑️  Delete 'georgy' folder? (y/n): ").strip().lower()
        if response == 'y':
            cleanup_folder(georgy_folder)
            print("\n✅ Setup complete! Ready to use face recognition.\n")
        else:
            print("\n⚠️  Keep folder for reference.")
            print("   Embeddings are stored in: face_embeddings.json")
            print("   Folder can be safely deleted later")
    else:
        print("\n❌ Failed to generate embeddings. Check folder contents.\n")
