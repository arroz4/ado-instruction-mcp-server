"""
Configuration and environment setup for ADO Instructions MCP Server

This module handles environment variables, external tool configuration,
and system setup requirements.
"""

import os
from pathlib import Path
from typing import Optional


def setup_environment():
    """Setup environment variables and configuration for local and Azure Container Apps"""
    # Check if running in Azure Container Apps
    # Azure Container Apps sets CONTAINER_APP_NAME environment variable
    is_azure_container_app = (
        os.getenv('CONTAINER_APP_NAME') is not None or 
        os.getenv('CONTAINER_APP_REVISION') is not None or
        os.getenv('AZURE_OPENAI_ENDPOINT') is not None  # If Azure env vars are set, likely in cloud
    )
    
    if is_azure_container_app:
        print("🌐 Running in Azure Container Apps - using Azure environment variables")
        # Validate required environment variables are present
        required_env_vars = ['AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables in Azure: {', '.join(missing_vars)}")
            print("💡 Please configure these variables in your Azure Container App configuration")
        else:
            print("✅ All required Azure environment variables found")
    else:
        # Local development - try to load from .env file
        print("🏠 Running locally - checking for .env file")
        try:
            from dotenv import load_dotenv
            env_file = Path(__file__).parent.parent / '.env'
            if env_file.exists():
                load_dotenv(env_file)
                print("✅ Environment variables loaded from .env file")
            else:
                print("⚠️ No .env file found - checking system environment variables")
        except ImportError:
            print("⚠️ python-dotenv not installed, using system environment variables only")
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


def get_organization_context() -> dict:
    """Get organization context from models"""
    from .models import ORGANIZATION_CONTEXT
    return ORGANIZATION_CONTEXT


def get_environment_info() -> dict:
    """
    Get information about the current environment
    
    Returns:
        Dictionary containing environment information
    """
    is_azure_container_app = (
        os.getenv('CONTAINER_APP_NAME') is not None or 
        os.getenv('CONTAINER_APP_REVISION') is not None or
        os.getenv('AZURE_OPENAI_ENDPOINT') is not None
    )
    
    return {
        "environment": "azure_container_app" if is_azure_container_app else "local",
        "azure_container_app": is_azure_container_app,
        "container_app_name": os.getenv('CONTAINER_APP_NAME'),
        "azure_openai_configured": bool(os.getenv('AZURE_OPENAI_ENDPOINT') and os.getenv('AZURE_OPENAI_API_KEY')),
        "python_dotenv_available": True
    }
