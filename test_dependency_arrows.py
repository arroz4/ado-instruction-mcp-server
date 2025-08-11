#!/usr/bin/env python3
"""
Test script for dependency arrow analysis functionality
"""
import asyncio
import base64
import sys
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.image_processor import process_image_with_azure_openai, load_image_as_base64
from modules.ado_generator import generate_work_items_from_features
from modules.display_utils import print_ado_summary, get_quick_stats

def test_dependency_arrows():
    """Test the enhanced dependency arrow analysis"""
    
    print("🔍 Testing Enhanced Dependency Arrow Analysis")
    print("=" * 50)
    
    # Test image path
    image_path = r"c:\Users\omarb\OneDrive\Escritorio\TestImageOmar\Diapositiva2.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return
    
    try:
        # Load and encode image
        image_base64 = load_image_as_base64(image_path)
        print(f"✅ Image loaded successfully")
        
        # Process with Azure OpenAI
        print("\n🧠 Processing with Azure OpenAI (dependency-aware)...")
        result = process_image_with_azure_openai(
            image_base64, 
            "Workflow diagram showing dependencies with arrows"
        )
        
        # Quick stats check
        stats = get_quick_stats(result)
        print(f"\n📊 Quick Analysis:")
        print(f"   Status: {stats['status']}")
        print(f"   Structure: {stats['epics']} Epic(s) → {stats['tasks']} Task(s)")
        print(f"   Proper dependency structure: {'✅ Yes' if stats['is_proper_structure'] else '❌ No'}")
        
        return result
                
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dependency_arrows()
