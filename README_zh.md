# Docker 镜像下载工具

一个用于从 Docker 仓库下载镜像并导出为 tar 归档文件以供离线使用的 Python 工具。

[变更历史](CHANGE_HISTORY.md) | [开发规范](DEVELOPMENT_GUIDELINES.md) | [English README](README.md)

## 功能特性

- 从任意 Docker 仓库下载镜像（默认为 Docker Hub）
- 支持多架构镜像（自动选择 amd64 架构）
- 支持直接使用镜像名称或 `docker pull` 命令作为输入
- 导出与 `docker load` 兼容的 tar 文件
- **智能缓存**：使用镜像摘要（digest）跳过已下载的镜像
- **交互式导入**：提供 Bash 脚本轻松导入镜像并自动清理
- 可配置的代理支持
- 可自定义输出目录

## 系统要求

- Python 3.7+
- 依赖管理使用 [uv](https://github.com/astral-sh/uv)

## 安装

1. 克隆仓库：
```bash
git clone <repository-url>
cd python_uv_docker_images
```

2. 使用 uv 安装依赖：
```bash
uv sync
```

或手动安装：
```bash
pip install requests pyyaml urllib3
```

## 配置

编辑 `config.yml` 来自定义设置：

```yaml
# 代理设置
proxy:
  enabled: true
  http: "http://localhost:10808"
  https: "http://localhost:10808"

# Docker 仓库配置
registry:
  default: "registry-1.docker.io"
  auth_url: "https://auth.docker.io/token"
  service: "registry.docker.io"

# 输出设置
output:
  temp_dir: "tmp"
  output_dir: "images"
  tar_extension: ".tar"

# 架构选择
architecture:
  os: "linux"
  arch: "amd64"

# SSL 验证
ssl_verify: false

# 请求超时（秒）
request_timeout: 300
```

## 使用方法

### 下载 Docker 镜像

运行下载工具：
```bash
python docker_image_downloader.py
```

系统会提示你输入镜像名称。你可以使用：
- 简单镜像名称：`ubuntu:latest`
- 完整镜像路径：`library/ubuntu:22.04`
- Docker pull 命令：`docker pull jenkins/jenkins:2.563`
- 自定义仓库：`myregistry.com/myimage:v1.0`

下载的 tar 文件将保存到配置的输出目录中。

**智能缓存**：工具使用 Docker 镜像摘要（SHA256 签名）来识别唯一镜像。如果具有相同摘要的镜像已存在，将跳过下载并立即显示导入命令。

### 生成导入命令

下载镜像后，生成 docker load 命令：
```bash
python generate_import_commands.py
```

这将扫描输出目录并显示所有 `.tar` 文件的导入命令。

### 导入镜像

#### 方式一：使用交互式脚本（推荐）

交互式脚本提供了用户友好的方式来导入多个镜像：

```bash
# 添加执行权限（仅首次需要）
chmod +x import_images.sh

# 运行脚本
./import_images.sh
```

**功能特性：**
- 自动扫描当前目录下的 `.tar` 文件
- 显示带编号的文件列表和文件大小
- 通过编号选择要导入的镜像
- 自动检测 Docker 权限（必要时使用 sudo）
- 成功导入后提示删除 tar 文件（默认：是）
- 每次操作后刷新文件列表
- 持续运行直到所有镜像导入或用户退出

**示例：**
```
======================================================================
  Docker Image Import Tool
======================================================================

Found 2 Docker image archive(s):
----------------------------------------------------------------------
1. library_redis_8.2.6_e2d3c0aeec38.tar (134.78 MB)
2. library_jenkins_2.563_f7e8d9c0b1a2.tar (681.75 MB)
----------------------------------------------------------------------
0. Exit

Enter number to import (0 to exit): 1

Importing: library_redis_8.2.6_e2d3c0aeec38.tar
----------------------------------------------------------------------
Loaded image: redis:8.2.6

✓ Successfully imported: library_redis_8.2.6_e2d3c0aeec38.tar

Delete library_redis_8.2.6_e2d3c0aeec38.tar? (Y/n, default: Y): 
✓ Deleted: library_redis_8.2.6_e2d3c0aeec38.tar
```

#### 方式二：手动导入

在目标机器上导入镜像：
```bash
docker load -i library_redis_8.2.6_e2d3c0aeec38.tar
```

或使用 sudo：
```bash
sudo docker load -i library_redis_8.2.6_e2d3c0aeec38.tar
```

验证导入：
```bash
docker images
```

## 项目结构

```
python_uv_docker_images/
├── config.yml                       # 配置文件
├── docker_image_downloader.py       # 主下载脚本
├── generate_import_commands.py      # 导入命令生成器
├── import_images.sh                 # 交互式导入脚本（Linux/Mac）
├── utils.py                         # 共享工具函数
├── logger_config.py                 # 日志配置
├── pyproject.toml                   # Python 项目元数据
├── uv.lock                          # 依赖锁定文件
├── README.md                        # 英文文档
├── README_zh.md                     # 中文文档
├── CHANGE_HISTORY.md                # 变更日志
├── DEVELOPMENT_GUIDELINES.md        # 开发和文档规范
├── images/                          # tar 文件输出目录
├── tmp/                             # 临时提取目录
└── logs/                            # 日志文件
```

## 工作原理

1. **身份验证**：从 Docker 仓库获取访问令牌
2. **获取清单**：检索镜像清单并选择合适的架构（默认 amd64）
3. **摘要检查**：获取镜像摘要（SHA256 签名）并检查是否已下载
4. **层下载**：按顺序下载每个层 blob，带进度日志（如果未缓存）
5. **镜像组装**：创建 Docker 兼容的 tar 归档文件，包含：
   - 层文件（从 gzip 解压缩）
   - 镜像配置元数据
   - 清单信息
   - 仓库标签
6. **导出**：将最终 tar 文件（文件名包含版本标签和摘要）保存到输出目录
7. **清理**：导出后自动删除临时文件

## 注意事项

- 工具自动处理多架构清单并选择 amd64
- **Tar 文件名包含版本标签和摘要**，便于识别（例如：`library_redis_8.2.6_e2d3c0aeec38.tar`）
- **镜像摘要用作唯一标识符** - 防止重复下载相同镜像
- 如果存在具有相同摘要的镜像，将自动跳过下载
- 导入脚本（`import_images.sh`）自动检测 Docker 权限并在必要时使用 sudo
- 为避免 sudo 提示，将用户添加到 docker 组：`sudo usermod -aG docker $USER`
- 层下载时会在控制台和日志文件中记录进度
- 导出后自动清理临时文件
- 默认禁用 SSL 验证以支持自签名仓库
- 兼容所有 Linux 发行版和 macOS
- 所有详细日志都保存在 `logs/` 目录中，带有时间戳

## 未来增强功能

以下功能正在计划中或考虑用于未来版本：

### 远程部署
- **SFTP 传输**：通过 SFTP 自动上传 tar 文件到远程服务器
- **SSH 集成**：通过 SSH 在远程服务器上执行 `docker load` 命令
- **多服务器支持**：同时将镜像部署到多个目标服务器
- **连接配置**：保存和管理多个服务器连接配置

### 批量操作
- **批量下载**：从列表或 YAML 配置文件下载多个镜像
- **批量导入**：一键导入目录中的所有 tar 文件
- **并行下载**：并发下载多个镜像以提高处理速度

### 高级缓存
- **层级别缓存**：在不同镜像之间复用层以节省带宽
- **本地仓库**：将下载的镜像推送到本地 Docker 仓库
- **缓存管理**：查看、清理和管理缓存层的工具

### 镜像管理
- **镜像检查**：显示详细的镜像信息（大小、层、创建日期）
- **标签管理**：重命名或为导入的镜像添加额外标签
- **镜像比较**：比较两个镜像以查看层差异
- **导出格式**：支持额外的导出格式（OCI、压缩的 tar.gz）

### 自动化与 CI/CD
- **CI/CD 集成**：GitHub Actions 或 GitLab CI 工作流
- **Webhook 支持**：基于外部事件触发下载
- **定时下载**：类似 Cron 的定期镜像更新调度
- **API 接口**：用于程序化访问的 REST API

### 监控与报告
- **下载统计**：跟踪带宽使用和下载时间
- **进度仪表板**：实时进度可视化
- **邮件通知**：下载完成或失败时发出警报
- **审计日志**：全面记录所有操作

### 安全增强
- **镜像验证**：验证镜像签名和校验和
- **漏洞扫描**：与安全扫描器集成（Trivy、Clair）
- **加密存储**：为敏感镜像加密 tar 文件
- **访问控制**：多用户环境的基于角色的访问控制

### 用户体验
- **GUI 应用**：带图形界面的桌面应用程序
- **交互模式**：带菜单的增强型 TUI（终端用户界面）
- **自动补全**：命令和镜像名称的 Shell 补全
- **配置向导**：首次用户的交互式设置

欢迎为这些功能贡献想法或实现！

## 许可证

MIT License

