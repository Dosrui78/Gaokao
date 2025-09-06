FROM python:3.13-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml .

# 安装项目依赖（使用--no-deps避免依赖冲突）
RUN pip install --no-cache-dir -e . --no-deps && \
    pip install --no-cache-dir curl-cffi loguru prefect pymongo requests tenacity

# 复制项目代码
COPY . .

# 设置Prefect API URL
ENV PREFECT_API_URL="http://129.204.227.156:4200/api"

# 启动命令
CMD ["prefect", "worker", "start", "--pool", "gaokao_pool"]