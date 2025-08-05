FROM python:3.13-slim

# 安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装 uv
RUN pip install uv

# 复制 pyproject.toml
COPY pyproject.toml ./

# 使用 uv 安装依赖
RUN uv pip install --system .

# 复制项目文件
COPY . /app
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app

# 启动命令
CMD ["python", "start.py"]