# logseq-mcp

Logseq 知识库的 MCP 服务器，提供完整的块、页面、查询和图谱操作。

## 业务逻辑框架

```
┌─────────────────────────────────────────────────────
│                   Entry Layer                        
│  ├── server.py (MCP stdio server)                   
│  └── client/cli.py (CLI)                         
├─────────────────────────────────────────────────────
│                   Handlers Layer                      
│  ├── tools.py  (MCP 工具处理)                        
│  └── prompts.py  (MCP 提示处理)                        
├─────────────────────────────────────────────────────
│                  Services Layer                       
│  ├── blocks.py  (块操作)                          
│  ├── pages.py   (页面操作)                           
│  ├── queries.py (查询操作)                           
│  └── graph.py   (图谱操作)                           
├─────────────────────────────────────────────────────
│                  Domain Layer                        
│  ├── models/schemas.py   (输入/输出模型)                     
│  └── models/enums.py     (枚举定义)                           
├─────────────────────────────────────────────────────
│                  Infrastructure Layer                  
│  ├── client/logseq.py  (HTTP API 客户端)                    
│  ├── client/base.py      (基础 HTTP 客户端)                 
│  └── config/settings.py  (配置管理)                          
└─────────────────────────────────────────────────────
```

## 核心服务

### 1. Block Service (`blocks.py`)

**业务逻辑**: 块的 CRUD 操作

**实现细节**:
- `BlockService.insert()` - 插入新块
  - 支持页面级块（`isPageBlock`）
  - 支持在父块之前插入（`before`）
  - 支持自定义 UUID（`customUUID`）
  - 支持块属性（`properties`）
- `BlockService.update()` - 更新块内容
  - 更新内容和可选属性
- `BlockService.delete()` - 删除块
- `BlockService.get()` - 通过 UUID 获取块
- `BlockService.move()` - 移动块
  - 支持移动为子块（`asChild`）
- `BlockService.insert_batch()` - 批量插入块

**参数** (默认值):
| 参数 | 默认值 | 说明 |
|------|---------|------|
| `parent_block` | - | 父块 UUID 或页面名称 |
| `content` | - | 块内容（支持 Markdown 格式） |
| `is_page_block` | `False` | 作为页面级块 |
| `before` | `False` | 在父块之前插入 |
| `custom_uuid` | `None` | 自定义 UUID |
| `properties` | `{}` | 块属性（JSON 格式） |
| `as_child` | `False` | 移动为子块 |

### 2. Page Service (`pages.py`)

**业务逻辑**: 页面管理操作

**实现细节**:
- `PageService.create()` - 创建新页面
  - 支持日记页面（`journal`）
  - 支持 markdown/org 格式
  - 可选创建初始块（`createFirstBlock`）
  - 支持页面属性
- `PageService.get()` - 获取页面
  - 支持包含子块（`includeChildren`）
- `PageService.delete()` - 删除页面
- `PageService.rename()` - 重命名页面
- `PageService.get_all()` - 列出所有页面

**参数** (默认值):
| 参数 | 默认值 | 说明 |
|------|---------|------|
| `page_name` | - | 页面名称 |
| `properties` | `{}` | 页面属性（JSON 格式） |
| `journal` | `False` | 创建为日记页面 |
| `format` | `"markdown"` | 页面格式（`markdown` 或 `org`） |
| `create_first_block` | `True` | 创建初始空块 |
| `include_children` | `False` | 是否包含子块 |

### 3. Query Service (`queries.py`)

**业务逻辑**: 查询操作

**实现细节**:
- `QueryService.simple_query()` - 简单查询
  - 支持标签查询（`[[tag]]`）
  - 支持属性查询（`#property`）
  - 支持高级查询语法（`{{query ...}}`）
- `QueryService.advanced_query()` - Datascript 查询
  - 支持输入参数（`inputs`）
- `QueryService.get_tasks()` - 获取任务
  - 按标记过滤（`marker`）
  - 按优先级过滤（`priority`）

**参数** (默认值):
| 参数 | 默认值 | 说明 |
|------|---------|------|
| `query` | - | 查询字符串 |
| `inputs` | `[]` | Datascript 输入参数（JSON 格式） |
| `marker` | - | 任务标记（如 `TODO`, `DOING`, `DONE`） |
| `priority` | - | 任务优先级（`A`, `B`, `C`） |

### 4. Graph Service (`graph.py`)

**业务逻辑**: 图谱和 Git 操作

**实现细节**:
- `GraphService.get_current_graph()` - 获取当前图谱信息
- `GraphService.get_user_configs()` - 获取用户配置
- `GraphService.git_commit()` - Git 提交
- `GraphService.git_status()` - Git 状态

**参数** (默认值):
| 参数 | 默认值 | 说明 |
|------|---------|------|
| `message` | - | Git 提交消息 |

**功能开关**: 通过环境变量 `LOGSEQ_ENABLE_GIT_OPERATIONS` 控制（默认：`false`）

## CLI 命令

### 启动服务器
```bash
logseq-mcp

# 或指定环境变量
LOGSEQ_API_TOKEN=your_token LOGSEQ_API_URL=http://localhost:12315 logseq-mcp
```

### 块操作
```bash
# 插入块
logseq-mcp blocks insert --parent "Page Name" --content "- 新块内容"

# 更新块
logseq-mcp blocks update --uuid <uuid> --content "更新后的内容"

# 删除块
logseq-mcp blocks delete --uuid <uuid>

# 移动块
logseq-mcp blocks move --uuid <uuid> --target <target-uuid> --as-child

# 批量插入
logseq-mcp blocks batch-insert --parent "Page Name" --file blocks.json

# 获取页面所有块
logseq-mcp blocks get-page-blocks --page "Page Name"
```

### 页面操作
```bash
# 创建页面
logseq-mcp pages create --name "新页面名称"

# 获取页面
logseq-mcp pages get --name "页面名称"

# 列出所有页面
logseq-mcp pages get-all

# 删除页面
logseq-mcp pages delete --name "页面名称"

# 重命名页面
logseq-mcp pages rename --old "旧名称" --new "新名称"
```

### 查询操作
```bash
# 简单查询
logseq-mcp queries simple --query "[[tag]]"

# Datascript 查询
logseq-mcp queries advanced --query "[:find ...]"

# 获取任务
logseq-mcp queries get-tasks --marker TODO

# 按优先级获取任务
logseq-mcp queries get-tasks --marker TODO --priority A
```

### 图谱操作
```bash
# 获取图谱信息
logseq-mcp graph info

# Git 提交
logseq-mcp graph git-commit --message "提交消息"

# Git 状态
logseq-mcp graph git-status
```

## 环境变量

### 连接配置
| 变量 | 默认值 | 说明 |
|------|---------|------|
| `LOGSEQ_API_TOKEN` | - | Logseq API 授权令牌（必需） |
| `LOGSEQ_API_URL` | `http://localhost:12315` | API endpoint |
| `LOGSEQ_API_TIMEOUT` | `10` | 请求超时（秒） |
| `LOGSEQ_API_MAX_RETRIES` | `3` | 最大重试次数 |

### 功能开关
| 变量 | 默认值 | 说明 |
|------|---------|------|
| `LOGSEQ_ENABLE_ADVANCED_QUERIES` | `true` | 启用高级查询和任务工具 |
| `LOGSEQ_ENABLE_GIT_OPERATIONS` | `false` | 启用 Git 操作 |

## MCP 工具

### 块操作（8 工具）
- `logseq_insert_block` - 创建块
- `logseq_update_block` - 更新块
- `logseq_delete_block` - 删除块
- `logseq_get_block` - 获取块
- `logseq_move_block` - 移动块
- `logseq_insert_batch` - 批量插入块
- `logseq_get_page_blocks` - 获取页面所有块
- `logseq_get_current_page_content` - 获取当前页面内容

### 页面操作（5 工具）
- `logseq_create_page` - 创建页面
- `logseq_get_page` - 获取页面
- `logseq_delete_page` - 删除页面
- `logseq_rename_page` - 重命名页面
- `logseq_get_all_pages` - 列出所有页面

### 查询操作（4 工具）
- `logseq_simple_query` - 简单查询
- `logseq_advanced_query` - Datascript 查询
- `logseq_get_tasks` - 获取任务

### 图谱操作（2 工具）
- `logseq_get_current_graph` - 获取图谱信息
- `logseq_get_user_configs` - 获取用户配置

### Git 操作（2 工具，需开关）
- `logseq_git_commit` - Git 提交
- `logseq_git_status` - Git 状态

## 安装

```bash
cd logseq-mcp
uv sync
```

**要求**: Python 3.12+, uv

## Claude Desktop 配置

```json
{
  "mcpServers": {
    "logseq": {
      "command": "uv",
      "args": ["--directory", "/path/to/logseq-mcp", "run", "logseq-mcp"],
      "env": {
        "LOGSEQ_API_TOKEN": "your_logseq_api_token"
      }
    }
  }
}
```
