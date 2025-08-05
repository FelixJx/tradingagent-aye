#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Trading Agent Configuration for Render Deployment
"""

import os

class SimpleConfig:
    """Simplified configuration for web deployment"""
    
    def __init__(self):
        pass
    
    @property
    def tushare_token(self):
        return os.getenv('TUSHARE_TOKEN', '')
    
    @property
    def dashscope_api_key(self):
        return os.getenv('DASHSCOPE_API_KEY', '')
    
    @property
    def deepseek_api_key(self):
        return os.getenv('DEEPSEEK_API_KEY', '')
    
    @property
    def tavily_api_key(self):
        return os.getenv('TAVILY_API_KEY', '')
    
    @property
    def flask_host(self):
        return os.getenv('FLASK_HOST', '0.0.0.0')
    
    @property
    def flask_port(self):
        try:
            return int(os.getenv('PORT', 5000))  # Render uses PORT env var
        except (ValueError, TypeError):
            return 5000
    
    @property
    def flask_debug(self):
        return os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

def get_simple_config():
    """Get simple configuration instance"""
    return SimpleConfig()