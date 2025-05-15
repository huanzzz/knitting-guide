import os
from pathlib import Path
import json

class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.knitting_config'
        self.config_file = self.config_dir / 'config.json'
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        """确保配置目录和文件存在"""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.config_file.write_text('{}')

    def get_api_key(self) -> str:
        """获取API密钥"""
        config = self._load_config()
        return config.get('openai_api_key', '')

    def set_api_key(self, api_key: str):
        """设置API密钥"""
        config = self._load_config()
        config['openai_api_key'] = api_key
        self._save_config(config)

    def _load_config(self) -> dict:
        """加载配置文件"""
        try:
            return json.loads(self.config_file.read_text())
        except json.JSONDecodeError:
            return {}

    def _save_config(self, config: dict):
        """保存配置到文件"""
        self.config_file.write_text(json.dumps(config, indent=2))

# 创建全局配置实例
config = Config()

def get_api_key() -> str:
    """获取API密钥的便捷函数"""
    return config.get_api_key()

def set_api_key(api_key: str):
    """设置API密钥的便捷函数"""
    config.set_api_key(api_key) 