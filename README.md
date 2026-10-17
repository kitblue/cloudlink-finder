# 网盘资源搜索神器（离线版）

CloudLink Finder 是一个面向互联网公开分享链接的多网盘资源聚合搜索工具。它支持夸克网盘、百度网盘、阿里云盘、迅雷网盘等主流网盘，并提供链接有效性检测、标题匹配、网盘筛选、提取码复制和新页面打开等功能。

本项目提供 **飞牛 fnOS 离线安装包（Docker 镜像内置版）**：安装包内已内置应用 Docker 镜像，安装时自动加载，全程无需连接 Docker Hub，适用于无法稳定访问 Docker Hub 的网络环境。

## 功能特性

- 🔍 **结构化多源搜索**：使用内置的公开网盘聚合索引，并保留严格的搜狗/Bing 兜底源
- 📦 **支持 9 种网盘**：夸克、百度、阿里、迅雷、天翼、UC、115、123、移动云盘
- ✅ **链接有效性验证**：返回前调用网盘公开接口确认链接状态和实际资源标题
- 🎯 **标题与链接准确绑定**：每条分享链接保留独立标题，过滤张冠李戴的结果
- 🧭 **指定网盘搜索**：可以只搜索选定的网盘类型
- 📋 **复制并打开**：复制链接或链接及提取码后，在新页签或新窗口打开网盘页面
- 🎨 **暗色模式**：支持亮色、暗色和跟随系统三种主题
- 📱 **响应式设计**：同时适配桌面端和移动端
- ⚡ **搜索缓存**：相同关键词在短时间内使用缓存，加快重复搜索
- 🔧 **可扩展搜索源**：支持通过配置添加自定义搜索 API

## 飞牛 fnOS 使用方式

| 安装方式 | 适用场景 | 安装入口 |
|---|---|---|
| 应用商店源安装（推荐） | 飞牛 fnOS 用户，一键安装并自动跟随版本更新 | 应用中心 → 应用商店源 |
| 手动安装 FPK | 已下载离线安装包，或不想添加商店源 | 应用中心 → 手动安装 |

如果你使用的是飞牛 NAS，推荐使用应用商店源安装：后续发布新版本会自动推送到应用中心，无需手动下载。

### 方式一：应用商店源安装（推荐）

本仓库自带应用商店源文件 `fnpack.json`，可直接添加为自更新源：新版本发布后本源自动更新，应用中心无需重复操作即可获得后续版本。

1. 打开飞牛 fnOS 应用中心。
2. 进入“应用商店源”管理，添加本源地址：`https://raw.githubusercontent.com/kitblue/cloudlink-finder/main/fnpack.json`
3. 刷新商店源列表，搜索“网盘搜索神器”或 `cloudlink-finder`。
4. 点击安装。安装包为离线版（Docker 镜像已内置），安装过程不访问 Docker Hub。

### 方式二：手动安装 FPK

#### 环境要求

- 飞牛 fnOS `1.1.3100` 或更高版本
- 已启用 Docker 服务
- 默认端口 `8899` 未被其他应用占用
- 无需访问 Docker Hub（镜像已内置在安装包中）

FPK 的应用标识为：

```text
cloudlink-finder
```

当前包声明支持平台：

```text
x86
```

#### 1. 获取离线 FPK 安装包

从本仓库 Release 页下载最新安装包：

```text
cloudlink-finder-<版本号>-offline.fpk
```

- [GitHub Release 页](https://github.com/kitblue/cloudlink-finder/releases)

`-offline` 后缀表示该安装包为 Docker 镜像内置版，安装全程无需联网拉取镜像。

#### 2. 在飞牛应用中心安装

1. 登录飞牛 fnOS 管理界面。
2. 打开“应用中心”。
3. 点击“手动安装”。
4. 选择并上传 `cloudlink-finder-<版本号>-offline.fpk`。
5. 阅读权限和端口提示，确认安装。
6. 应用中心会自动加载安装包内内置的 Docker 镜像并启动应用，无需联网拉取镜像。

#### 3. 打开应用

安装成功后，可以使用以下任一方式访问：

- 点击飞牛桌面的“网盘搜索神器”图标，系统会在浏览器窗口中打开应用。
- 在浏览器中直接访问：

```text
http://飞牛NAS-IP:8899
```

例如飞牛 NAS 的地址是 `192.168.1.20`：

```text
http://192.168.1.20:8899
```

#### 4. 数据目录和升级说明

当前 FPK 的持久化数据目录为：

```text
/var/apps/cloudlink-finder/shares/cloudlink-finder/data
```

升级前建议备份该目录。正常版本升级应保持应用标识 `cloudlink-finder` 不变，以便复用原有应用数据。

早期测试包曾使用应用标识 `third-pan-search`。如果设备上仍安装着该旧包，建议先备份旧数据并卸载旧包，再安装当前 `cloudlink-finder` 包，避免端口和容器冲突。旧数据目录不会自动迁移到新应用目录。

## 开发环境

如果需要分别启动前后端进行开发：

### 后端

```bash
cd backend
python3 -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | Vue 3 + TypeScript + Vite |
| 后端 | Python FastAPI |
| 数据库 | SQLite |
| 容器 | Docker + Nginx + Supervisor（离线包镜像已内置） |
| 飞牛打包 | fnpack + FPK |

## 搜索源说明

应用默认使用内置的公开网盘聚合源，并将搜狗、Bing 作为严格兜底源。一个搜索卡片内出现多个链接时不会猜测标题归属；无法通过网盘公开接口确认有效性的链接也不会进入严格结果。

可以通过后端配置文件 `data/sources.yaml` 添加自定义 API 搜索源。

## 质量保证

当前对夸克、百度、阿里、123 网盘执行严格有效性检测。搜索缓存命中时仍会按短周期重新确认链接状态；外部节点临时失败时会重试，并可回退到全量搜索后在本地按网盘类型过滤。

## 支持网盘

| 网盘 | 域名 |
|---|---|
| 夸克网盘 | `pan.quark.cn` |
| 百度网盘 | `pan.baidu.com` |
| 阿里云盘 | `aliyundrive.com` |
| 迅雷网盘 | `pan.xunlei.com` |
| 天翼云盘 | `cloud.189.cn` |
| UC 网盘 | `drive.uc.cn` |
| 115 网盘 | `115.com` |
| 123 云盘 | `123pan.com` |
| 移动云盘 | `caiyun.139.com` |

## 项目仓库

- 离线版发布仓库：[kitblue/cloudlink-finder](https://github.com/kitblue/cloudlink-finder)（本仓库，Release 提供内置 Docker 镜像的离线 FPK）
- 上游项目：[jindekun520-dev/cloudlink-finder](https://github.com/jindekun520-dev/cloudlink-finder)（功能与代码上游，本仓库自动跟随其新版本）
- 应用商店源：本源 `fnpack.json`（本仓库根目录，自更新源）

## 自动更新说明

本仓库通过 GitHub Actions 自动跟随上游 `jindekun520-dev/cloudlink-finder` 的新版本：检测到上游发布新版本后自动同步代码、构建内置镜像的离线 FPK、发布 Release，并自动更新本源 `fnpack.json`（本仓库根目录的应用商店源，版本、下载地址、sha256）。作为自更新源，添加本源后应用中心将自动获得后续更新。

## 使用说明

本应用只聚合检索互联网上已经公开的网盘分享信息，不提供资源上传、存储或下载服务，也不会要求或保存用户的网盘账号和密码。请遵守所在地法律法规、网盘平台规则以及内容版权要求，合理使用搜索结果。
