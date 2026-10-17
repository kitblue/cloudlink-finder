"""
应用设置API
提供搜索源启用状态与默认筛选网盘类型的持久化读写
"""
import json
import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.settings import AppSetting
from app.services.searcher import orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["设置"])

SEARCH_SOURCES_KEY = "search_sources"
DEFAULT_TYPES_KEY = "default_types"


class SettingsUpdate(BaseModel):
    """设置更新请求"""

    search_sources: Optional[Dict[str, bool]] = None
    default_types: Optional[List[str]] = None


async def _read_setting(db: AsyncSession, key: str) -> Optional[str]:
    result = await db.execute(select(AppSetting).where(AppSetting.key == key))
    row = result.scalar_one_or_none()
    return row.value if row else None


async def _write_setting(db: AsyncSession, key: str, value: str):
    result = await db.execute(select(AppSetting).where(AppSetting.key == key))
    row = result.scalar_one_or_none()
    if row:
        row.value = value
    else:
        db.add(AppSetting(key=key, value=value))
    await db.commit()


async def get_persisted_search_sources(db: AsyncSession) -> Dict[str, bool]:
    """读取持久化的搜索源启用状态覆盖"""
    raw = await _read_setting(db, SEARCH_SOURCES_KEY)
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return {str(k): bool(v) for k, v in data.items()}
    except json.JSONDecodeError:
        logger.warning("app_settings.search_sources 解析失败，忽略")
    return {}


async def apply_persisted_settings(db: AsyncSession):
    """将持久化的搜索源启用状态应用到 orchestrator（服务启动时调用）"""
    enabled_map = await get_persisted_search_sources(db)
    orchestrator.apply_settings(enabled_map)


@router.get("")
async def get_settings(db: AsyncSession = Depends(get_db)):
    """获取应用设置：搜索源启用状态与默认筛选网盘类型"""
    enabled_map = await get_persisted_search_sources(db)
    actual = {s["name"]: s["enabled"] for s in orchestrator.get_sources()}
    # 持久化覆盖兜底合并（防御 orchestrator 尚未应用的情况）
    actual.update(enabled_map)

    raw_types = await _read_setting(db, DEFAULT_TYPES_KEY)
    default_types: List[str] = []
    if raw_types:
        try:
            data = json.loads(raw_types)
            if isinstance(data, list):
                default_types = [str(t) for t in data]
        except json.JSONDecodeError:
            pass

    return {
        "code": 0,
        "data": {
            "search_sources": actual,
            "default_types": default_types,
        },
    }


@router.put("")
async def update_settings(
    payload: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新应用设置"""
    if payload.search_sources is not None:
        existing = await get_persisted_search_sources(db)
        existing.update(payload.search_sources)
        await _write_setting(
            db, SEARCH_SOURCES_KEY, json.dumps(existing, ensure_ascii=False)
        )
        orchestrator.apply_settings(existing)

    if payload.default_types is not None:
        await _write_setting(
            db, DEFAULT_TYPES_KEY, json.dumps(payload.default_types, ensure_ascii=False)
        )

    return await get_settings(db)
