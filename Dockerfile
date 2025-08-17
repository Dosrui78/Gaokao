FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件（至少包含你的部署配置文件 my_file.yaml）
COPY prefect.yaml .

# 安装 uv
RUN pip install uv

# 复制 pyproject.toml
COPY pyproject.toml .

# 使用 uv 安装依赖
RUN uv pip install --system .

# 设置环境变量（如需连接 Prefect 服务器，指定 API 地址）
ENV PREFECT_API_URL="http://129.204.227.156:4200/api"

# 容器启动时执行部署命令
CMD ["sh", "-c", "prefect deploy --prefect-file prefect.yaml && prefect worker start --pool gaokao_pool"]