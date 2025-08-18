FROM python:3.13-slim

# 安装 git 并切换 Debian 源（slim 可能没有 /etc/apt/sources.list）
RUN set -eux; \
    . /etc/os-release; \
    printf "Types: deb\nURIs: https://mirrors.tuna.tsinghua.edu.cn/debian\nSuites: %s %s-updates %s-backports\nComponents: main contrib non-free non-free-firmware\n\nTypes: deb\nURIs: https://mirrors.tuna.tsinghua.edu.cn/debian-security\nSuites: %s-security\nComponents: main contrib non-free non-free-firmware\n" "$VERSION_CODENAME" "$VERSION_CODENAME" "$VERSION_CODENAME" "$VERSION_CODENAME" > /etc/apt/sources.list.d/debian.sources; \
    apt-get update; \
    apt-get install -y --no-install-recommends git ca-certificates; \
    rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install --no-cache-dir uv

# 使用国内镜像源（uv 与 pip 均生效）
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/

# 先复制依赖定义文件，利用缓存
WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .

# 用 uv 按锁文件安装到系统环境
RUN uv sync --frozen --no-dev --system

# 复制项目代码
COPY . /app

# 启动命令
CMD ["prefect", "worker", "start", "--pool", "gaokao_pool"]