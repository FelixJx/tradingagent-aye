#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Agent Configuration Management
Secure handling of environment variables and API keys
"""

import os
from typing import Optional, Dict, Any
import logging

# Try to load dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables only")

class Config:
    """Configuration management class for Trading Agent"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self._validate_required_env_vars()
    
    @staticmethod
    def _setup_logging() -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
        return logger
    
    def _validate_required_env_vars(self) -> None:
        """Validate that required environment variables are set"""
        required_vars = [
            'TUSHARE_TOKEN',
            'DASHSCOPE_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.warning(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            self.logger.warning(
                "Please check your .env file or set these variables in your environment"
            )
    
    # API Configuration
    @property
    def tushare_token(self) -> Optional[str]:
        """Get Tushare API token"""
        return os.getenv('TUSHARE_TOKEN')
    
    @property
    def dashscope_api_key(self) -> Optional[str]:
        """Get DashScope API key"""
        return os.getenv('DASHSCOPE_API_KEY')
    
    @property
    def deepseek_api_key(self) -> Optional[str]:
        """Get DeepSeek API key"""
        return os.getenv('DEEPSEEK_API_KEY')
    
    @property
    def tavily_api_key(self) -> Optional[str]:
        """Get Tavily API key"""
        return os.getenv('TAVILY_API_KEY')
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        return os.getenv('OPENAI_API_KEY')
    
    # Flask Configuration
    @property
    def flask_env(self) -> str:
        """Get Flask environment"""
        return os.getenv('FLASK_ENV', 'development')
    
    @property
    def flask_debug(self) -> bool:
        """Get Flask debug mode"""
        return os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    @property
    def secret_key(self) -> str:
        """Get Flask secret key"""
        return os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration
    @property
    def database_url(self) -> str:
        """Get database URL"""
        return os.getenv('DATABASE_URL', 'sqlite:///trading_agent.db')
    
    # Trading Configuration
    @property
    def default_market(self) -> str:
        """Get default stock market"""
        return os.getenv('DEFAULT_MARKET', 'SH')
    
    @property
    def max_position_size(self) -> float:
        """Get maximum position size"""
        return float(os.getenv('MAX_POSITION_SIZE', '0.1'))
    
    @property
    def stop_loss_ratio(self) -> float:
        """Get stop loss ratio"""
        return float(os.getenv('STOP_LOSS_RATIO', '0.05'))
    
    # Logging Configuration
    @property
    def log_level(self) -> str:
        """Get log level"""
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def log_file(self) -> str:
        """Get log file path"""
        return os.getenv('LOG_FILE', 'logs/trading_agent.log')
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration dictionary"""
        return {
            'tushare': {
                'token': self.tushare_token,
                'enabled': bool(self.tushare_token)
            },
            'dashscope': {
                'api_key': self.dashscope_api_key,
                'enabled': bool(self.dashscope_api_key)
            },
            'deepseek': {
                'api_key': self.deepseek_api_key,
                'enabled': bool(self.deepseek_api_key)
            },
            'tavily': {
                'api_key': self.tavily_api_key,
                'enabled': bool(self.tavily_api_key)
            },
            'openai': {
                'api_key': self.openai_api_key,
                'enabled': bool(self.openai_api_key)
            }
        }
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading configuration dictionary"""
        return {
            'default_market': self.default_market,
            'max_position_size': self.max_position_size,
            'stop_loss_ratio': self.stop_loss_ratio
        }
    
    def check_api_availability(self) -> Dict[str, bool]:
        """Check which APIs are available"""
        api_config = self.get_api_config()
        return {
            service: config['enabled'] 
            for service, config in api_config.items()
        }

# Global configuration instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance"""
    return config

# Helper function for backward compatibility
def get_env_or_default(key: str, default: Any = None) -> Any:
    """Get environment variable or return default value"""
    return os.getenv(key, default)

if __name__ == "__main__":
    # Test configuration
    config = get_config()
    print("=== Trading Agent Configuration ===")
    print(f"Flask Environment: {config.flask_env}")
    print(f"Debug Mode: {config.flask_debug}")
    print(f"Database URL: {config.database_url}")
    print(f"Default Market: {config.default_market}")
    print("\n=== API Availability ===")
    api_status = config.check_api_availability()
    for service, available in api_status.items():
        status = "✅ Available" if available else "❌ Not configured"
        print(f"{service.title()}: {status}")
    
    print("\n=== Trading Configuration ===")
    trading_config = config.get_trading_config()
    for key, value in trading_config.items():
        print(f"{key}: {value}")