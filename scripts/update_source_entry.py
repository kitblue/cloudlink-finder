#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新飞牛应用商店源中 cloudlink-finder 条目（不存在则创建）。

支持两种目标仓库：
- 默认：kitblue/fnthird 的 fnpack.json（第三方子源）
- 本仓库：kitblue/cloudlink-finder 的 fnpack.json（本项目自身即源）

环境变量:
  APP_VERSION    版本号（如 1.0.10，可带 v 前缀）
  APP_SHA256     fpk 的 sha256
  APP_SIZE       fpk 字节数
  TARGET_REPO    目标仓库（默认 kitblue/fnthird），如 kitblue/cloudlink-finder
  FNTHIRD_TOKEN  有目标仓库写权限的 PAT（workflow 中也可用 GITHUB_TOKEN）
"""
import os, sys, json, base64, urllib.request

TOKEN = os.environ.get('FNTHIRD_TOKEN') or os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    sys.exit('缺少 FNTHIRD_TOKEN 或 GITHUB_TOKEN')

VERSION = os.environ.get('APP_VERSION', '').lstrip('v')
SHA = os.environ.get('APP_SHA256', '').strip().lower()
SIZE = int(os.environ.get('APP_SIZE', '0') or 0)
if not VERSION or not SHA or not SIZE:
    sys.exit(f'参数不完整 VERSION={VERSION!r} SHA={SHA!r} SIZE={SIZE!r}')

REPO = os.environ.get('TARGET_REPO', 'kitblue/fnthird').strip()
PATH = 'fnpack.json'
API = 'https://api.github.com'
HDR = {'Authorization': f'token {TOKEN}', 'User-Agent': 'fnunify-sync', 'Accept': 'application/vnd.github+json'}


def req(url, method='GET', body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, method=method, headers=HDR, data=data)
    with urllib.request.urlopen(r, timeout=120) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else None


meta = req(f'{API}/repos/{REPO}/contents/{PATH}')
current = json.loads(base64.b64decode(meta['content']).decode('utf-8'))
apps = current.setdefault('apps', {})

base_entry = {
    'display_name': '网盘搜索神器',
    'desc': '多网盘资源聚合搜索工具：支持夸克、百度、阿里、迅雷等 9 种网盘的公开分享链接检索，提供链接有效性验证、标题匹配、网盘筛选、提取码复制、暗色模式与搜索缓存。离线版安装包已内置 Docker 镜像，安装无需连接 Docker Hub。',
    'platform': ['x86'],
    'categories': ['网络工具'],
    'icon_url': 'https://raw.githubusercontent.com/kitblue/cloudlink-finder/main/ICON.PNG',
    'distributor': 'kitblue',
    'distributor_url': 'https://github.com/kitblue',
    'author': 'jindekun520-dev',
    'author_url': 'https://github.com/jindekun520-dev',
    'developer': '',
    'publisher': '',
    'publisher_url': '',
    'run_as': 'package',
    'install_type': '',
    'is_docker': True,
    'service_port': '8899',
    'releases': {},
    'appname': 'cloudlink-finder',
    '_src': 'kitblue/cloudlink-finder',
}

entry = apps.get('cloudlink-finder')
if entry is None:
    entry = dict(base_entry)
else:
    for k, v in base_entry.items():
        entry.setdefault(k, v)

entry['releases'][VERSION] = {
    'packages': {
        'x86': {
            'download_url': f'https://github.com/kitblue/cloudlink-finder/releases/download/v{VERSION}/cloudlink-finder-{VERSION}-offline.fpk',
            'sha256': SHA,
            'size': SIZE,
        }
    }
}
apps['cloudlink-finder'] = entry

out = json.dumps(current, ensure_ascii=False, indent=2) + '\n'
req(f'{API}/repos/{REPO}/contents/{PATH}', 'PUT', {
    'message': f'add/update cloudlink-finder v{VERSION} (offline, Docker image built-in) [skip ci]',
    'content': base64.b64encode(out.encode('utf-8')).decode(),
    'sha': meta['sha'],
})
print(f'OK {REPO} 已更新: cloudlink-finder v{VERSION} sha256={SHA} size={SIZE}')
