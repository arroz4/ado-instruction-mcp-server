"""
Configuration and environment setup for ADO Instructions MCP Server

This module handles environment variables, external tool configuration,
and system setup requirements.
"""

import os
from pathlib import Path
from typing import Optional


def setup_environment():
    """Setup environment variables and configuration"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded from .env file")
    except ImportError:
        print("⚠️ python-dotenv not installed, skipping .env file loading")
    except Exception as e:
        print(f"⚠️ Error loading .env file: {e}")


def get_azure_openai_config() -> dict:
    """
    Get Azure OpenAI configuration from environment variables
    
    Returns:
        Dictionary containing Azure OpenAI configuration
    """
    config = {
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "o4-mini-imagebot"),
        "model": os.getenv("AZURE_OPENAI_MODEL", "o4-mini")
    }
    
    # Check if required config is present
    if config["endpoint"] and config["api_key"]:
        print("✅ Azure OpenAI configuration loaded successfully")
    else:
        print("⚠️ Azure OpenAI configuration incomplete. Image processing will be unavailable.")
        
    return config


def validate_azure_openai_config() -> bool:
    """
    Validate Azure OpenAI configuration
    
    Returns:
        True if configuration is valid, False otherwise
    """
    config = get_azure_openai_config()
    
    required_fields = ["endpoint", "api_key"]
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        print(f"❌ Missing Azure OpenAI configuration: {', '.join(missing_fields)}")
        return False
        
    # Validate endpoint format
    endpoint = config["endpoint"]
    if endpoint and not endpoint.startswith("https://"):
        print("❌ Azure OpenAI endpoint must start with https://")
        return False
        
    print("✅ Azure OpenAI configuration is valid")
    return True


def setup_tesseract():
    """Configure Tesseract OCR with fallback paths"""
    try:
        import pytesseract
        
        # Try to get Tesseract path from environment variable
        tesseract_cmd = os.getenv('tesseract_cmd')
        
        if tesseract_cmd and os.path.exists(tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            print(f"🔧 Tesseract configured from environment: {tesseract_cmd}")
            return True
        
        # Fallback to default Windows installation path
        default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(default_path):
            pytesseract.pytesseract.tesseract_cmd = default_path
            print(f"🔧 Tesseract found at default path: {default_path}")
            return True
        
        print("⚠️ Tesseract OCR not found. Please install Tesseract or set tesseract_cmd in .env file")
        return False
        
    except ImportError:
        print("⚠️ pytesseract not installed. Image OCR functionality will be limited.")
        return False
    except Exception as e:
        print(f"⚠️ Error setting up Tesseract: {e}")
        return False


def get_organization_context() -> dict:
    """Get organization context from models"""
    from .models import ORGANIZATION_CONTEXT
    return ORGANIZATION_CONTEXT
