"""
数据模型
"""
from app.models.cache import SearchCache
from app.models.history import SearchHistory
from app.models.settings import AppSetting

__all__ = ["SearchCache", "SearchHistory", "AppSetting"]
