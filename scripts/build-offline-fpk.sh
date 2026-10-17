#!/usr/bin/env bash
# ============================================================
# CloudLink Finder 离线 FPK 构建脚本
# 将预构建 Docker 镜像（docker save | gzip 产物）打进 fpk，
# 安装时由 cmd/install_init 执行 docker load，全程不依赖 Docker Hub。
#
# 用法:
#   1) 构建并导出镜像:
#        docker build -t cloudlink-finder:<ver> -f docker/Dockerfile .
#        docker save cloudlink-finder:<ver> | gzip > release/cloudlink-finder-<ver>.tar.gz
#   2) 组装 fpk:
#        IMAGE_TAR=release/cloudlink-finder-<ver>.tar.gz bash scripts/build-offline-fpk.sh
#    若 release/ 下已有 cloudlink-finder-*.tar.gz，可省略 IMAGE_TAR（自动发现）
# ============================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

APP_NAME="cloudlink-finder"
FNPACK_VERSION="1.2.3"

# ---- 从 manifest 读取版本 ----
VERSION="$(awk -F '=' '/^[[:space:]]*version[[:space:]]*=/ {gsub(/[[:space:]]/, "", $2); print $2}' fpk/manifest)"
if [ -z "$VERSION" ]; then
    echo "[error] 无法从 fpk/manifest 读取 version" >&2
    exit 1
fi
echo "[info] version = ${VERSION}"

# ---- 定位镜像 tar（docker save | gzip 产物） ----
IMAGE_TAR="${IMAGE_TAR:-}"
if [ -z "$IMAGE_TAR" ]; then
    IMAGE_TAR="$(ls release/cloudlink-finder-*.tar.gz 2>/dev/null | head -n1 || true)"
fi
if [ -z "$IMAGE_TAR" ] || [ ! -f "$IMAGE_TAR" ]; then
    echo "[error] 未找到镜像 tar。请先执行:" >&2
    echo "  docker build -t ${APP_NAME}:${VERSION} -f docker/Dockerfile ." >&2
    echo "  docker save ${APP_NAME}:${VERSION} | gzip > release/${APP_NAME}-${VERSION}.tar.gz" >&2
    echo "  IMAGE_TAR=release/${APP_NAME}-${VERSION}.tar.gz bash scripts/build-offline-fpk.sh" >&2
    exit 1
fi
echo "[info] image tar = ${IMAGE_TAR}"

# ---- 解析 fnpack（与 build-fpk.sh 同逻辑） ----
FNPACK="$(command -v fnpack || true)"
if [ -z "$FNPACK" ]; then
    FNPACK_DIR="${ROOT_DIR}/.tools"
    mkdir -p "$FNPACK_DIR"
    FNPACK="${FNPACK_DIR}/fnpack"
    if [ ! -x "$FNPACK" ]; then
        case "$(uname -s)-$(uname -m)" in
            Linux-x86_64|Linux-amd64)   FNPACK_OS_ARCH="linux-amd64" ;;
            Darwin-x86_64|Darwin-amd64) FNPACK_OS_ARCH="darwin-amd64" ;;
            Darwin-arm64)               FNPACK_OS_ARCH="darwin-arm64" ;;
            *) echo "[error] 不支持的平台 $(uname -s)-$(uname -m)" >&2; exit 1 ;;
        esac
        FNPACK_URL="https://static2.fnnas.com/share/mirrors/fnpack/fnpack-${FNPACK_VERSION}-${FNPACK_OS_ARCH}.tar.gz"
        echo "[info] 下载 fnpack ${FNPACK_VERSION} (${FNPACK_OS_ARCH}) ..."
        curl -fsSL "$FNPACK_URL" -o "${FNPACK_DIR}/fnpack.tar.gz"
        tar -xzf "${FNPACK_DIR}/fnpack.tar.gz" -C "$FNPACK_DIR"
        chmod +x "$FNPACK"
    fi
fi

# ---- 组装 staging 目录 ----
STAGING_DIR="${ROOT_DIR}/release/staging"
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"
cp -r fpk/. "$STAGING_DIR/"
cp ICON.PNG "$STAGING_DIR/ICON.PNG"
cp ICON_256.PNG "$STAGING_DIR/ICON_256.PNG"
mkdir -p "$STAGING_DIR/app/ui/images"
cp ICON.PNG "$STAGING_DIR/app/ui/images/cloudlink_finder_64.png"
cp ICON_256.PNG "$STAGING_DIR/app/ui/images/cloudlink_finder_256.png"

# 离线：源码与 Dockerfile 已打进镜像，fpk/app/docker 仅保留 compose + 镜像 tar
rm -f "$STAGING_DIR/app/docker/Dockerfile"
rm -rf "$STAGING_DIR/app/docker/backend" "$STAGING_DIR/app/docker/frontend" \
       "$STAGING_DIR/app/docker/nginx" "$STAGING_DIR/app/docker/supervisor" "$STAGING_DIR/app/docker/dist"

# compose 版本占位替换
sed -i "s/__VERSION__/${VERSION}/g" "$STAGING_DIR/app/docker/docker-compose.yaml"
# 镜像 tar 进包（gzip 压缩包直接内置，install_init 会 docker load）
cp "$IMAGE_TAR" "$STAGING_DIR/app/docker/${APP_NAME}-${VERSION}.tar.gz"

chmod 0755 "$STAGING_DIR"/cmd/* 2>/dev/null || true
chmod 0755 "$STAGING_DIR"/cmd/install/* 2>/dev/null || true
chmod 0755 "$STAGING_DIR"/cmd/upgrade/* 2>/dev/null || true
chmod 0755 "$STAGING_DIR"/cmd/uninstall/* 2>/dev/null || true
chmod 0755 "$STAGING_DIR"/cmd/config/* 2>/dev/null || true

# ---- fnpack 校验并构建 ----
echo "[info] fnpack build ..."
(cd "$STAGING_DIR" && "$FNPACK" build --directory "$STAGING_DIR")
BUILT_FPK="$(find "$ROOT_DIR/release" -name '*.fpk' -mmin -10 2>/dev/null | head -n1 || true)"
if [ -z "$BUILT_FPK" ]; then
    echo "[error] fnpack build 未产出 fpk" >&2
    exit 1
fi
FINAL_FPK="${ROOT_DIR}/release/${APP_NAME}-${VERSION}-offline.fpk"
cp "$BUILT_FPK" "$FINAL_FPK"
echo "[done] 离线 FPK 已生成: ${FINAL_FPK}"
echo "[hint] 安装时将自动 docker load ${APP_NAME}:${VERSION}，无需 Docker Hub。"
