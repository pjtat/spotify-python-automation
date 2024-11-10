import yaml
from pathlib import Path

class Config:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_config()
        return cls._instance
    
    @classmethod
    def _load_config(cls):
        config_path = Path(__file__).parent.parent / 'config.yaml'
        with open(config_path, 'r') as file:
            cls._config = yaml.safe_load(file)
    
    @classmethod
    def get(cls, *keys):
        if cls._config is None:
            cls._load_config()
            
        value = cls._config
        for key in keys:
            value = value[key]
        return value