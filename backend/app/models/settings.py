"""
应用设置模型
"""
import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AppSetting(Base):
    """应用设置（key-value 存储，value 为 JSON 字符串）"""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True, comment="设置键")
    value: Mapped[str] = mapped_column(Text, nullable=False, comment="设置值(JSON 字符串)")
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    def __repr__(self):
        return f"<AppSetting(key='{self.key}')>"
