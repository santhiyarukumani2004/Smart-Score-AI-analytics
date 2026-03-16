# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Base configuration class"""
    
    # Database configuration
    DB_NAME = os.getenv('DB_NAME', 'default_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '1000'))
    
    @property
    def DATABASE_URL(self):
        """Get database URL for SQLAlchemy"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DB_PARAMS(self):
        """Get database parameters as dictionary"""
        return {
            'dbname': self.DB_NAME,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'host': self.DB_HOST,
            'port': self.DB_PORT
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DB_NAME = os.getenv('DB_NAME_DEV', 'dev_db')

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    DB_NAME = os.getenv('DB_NAME_TEST', 'test_db')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DB_NAME = os.getenv('DB_NAME_PROD', 'prod_db')

# Select configuration based on environment
ENV = os.getenv('FLASK_ENV', 'development')

config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

config = config_map.get(ENV, DevelopmentConfig)()

# Create a global config instance
settings = config

