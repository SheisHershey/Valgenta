# LangChain 文档办公智能体 · 使用说明书

## 目录

- [一、项目概述](#一项目概述)
- [二、功能特性](#二功能特性)
- [三、技术栈](#三技术栈)
- [四、目录结构](#四目录结构)
- [五、环境部署](#五环境部署)
- [六、配置说明](#六配置说明)
- [七、快速开始](#七快速开始)
- [八、工具详解](#八工具详解)
- [九、架构原理](#九架构原理)
- [十、常见问题](#十常见问题)

---

## 一、项目概述

本项目是一个基于 **LangChain + LangGraph** 构建的文档办公智能体，专为论文写作、办公文档处理场景设计。智能体具备 **23 个工具**，覆盖文档读写、内容润色、结构提取、表格数据、论文排版、多格式转换、流程自动化、RAG 知识管理六大方向，能够自主调用工具完成复杂的办公任务。

核心能力：
- 读取/生成 Word、PDF、Excel 等办公文档
- 对文档进行润色、总结、翻译、语法检查
- 提取大纲、生成目录、格式化参考文献
- 文本查重、学术搜索、论文排版
- 批量处理文档、版本对比、邮件草稿生成
- 构建本地知识库，基于语义检索问答（RAG）

---

## 二、功能特性

| 能力方向 | 工具数量 | 说明 |
|---------|---------|------|
| 文档读写与内容处理 | 6 | 读取/生成 docx、PDF 读取、润色、总结、翻译、语法检查 |
| 文档结构增强 | 3 | 提取大纲、生成目录、格式化参考文献 |
| 表格与数据 | 3 | 读取 docx 表格、生成图表、Excel 数据分析 |
| 论文专项 | 3 | 文本相似度查重、arXiv 学术搜索、学术排版 |
| 多格式支持 | 2 | 格式转换（docx→md/txt）、PDF 文本提取 |
| 流程自动化 | 3 | 批量处理、版本对比、邮件草稿 |
| 知识管理 RAG | 3 | 构建知识库、语义检索、关键词提取 |

---

## 三、技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.13 |
| LLM 框架 | LangChain | ≥ 1.0.0 |
| 状态图引擎 | LangGraph（LangChain 内置） | ≥ 1.0.0 |
| LLM 客户端 | langchain-openai | ≥ 1.0.0 |
| 配置管理 | pydantic-settings | ≥ 2.0.0 |
| Word 处理 | python-docx | ≥ 1.0.0 |
| PDF 处理 | pdfplumber | ≥ 0.10.0 |
| Excel 处理 | openpyxl | ≥ 3.1.0 |
| 图表生成 | matplotlib | ≥ 3.7.0 |
| 文本向量化 | fastembed（bge-small-zh-v1.5） | ≥ 0.3.0 |
| 向量数据库 | Chroma | ≥ 0.4.0 |
| 文本分块 | langchain-text-splitters | ≥ 1.0.0 |

---

## 四、目录结构

```
agentframework/
├── langchainmain.py          # 主入口（演示三条执行通道）
├── main.py                   # 兼容入口（委托给 langchainmain）
├── config.py                 # 全局配置（pydantic-settings）
├── requirements.txt          # 依赖清单
│
├── core/                     # 核心基础设施
│   ├── llm.py                # ChatOpenAI 模型单例
│   ├── prompts.py            # 提示词模板
│   ├── chains.py             # LCEL 链（数据通道）
│   ├── docx_processor.py     # Word 文档读写引擎
│   ├── embeddings.py         # 本地文本向量化（fastembed）
│   └── vectorstore.py        # Chroma 向量库管理
│
├── agent/                    # 智能体
│   ├── agent.py              # 通用 Agent（LangGraph 状态图封装）
│   └── doc_agent.py          # 文档办公专用 Agent（23 个工具）
│
└── tools/                    # 工具集（共 23 个）
    ├── __init__.py           # 工具自动发现
    ├── document.py           # 基础文档工具
    ├── structure.py          # 文档结构增强
    ├── data.py               # 表格与数据
    ├── paper.py              # 论文专项
    ├── format.py             # 多格式支持
    ├── automation.py         # 流程自动化
    ├── knowledge.py          # 知识管理 RAG
    ├── calculator.py         # 计算器示例
    └── weather.py            # 天气查询示例
```

---

## 五、环境部署

### 5.1 环境要求

- Python ≥ 3.11
- Windows / macOS / Linux
- 网络可访问 LLM API 与 HuggingFace（首次下载 embedding 模型）

### 5.2 安装步骤

```bash
# 1. 克隆或进入项目目录
cd agentframework

# 2. 创建虚拟环境（推荐）
python -m venv .venv

# 3. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 5.3 验证安装

```bash
python -c "from agent.doc_agent import create_doc_agent; print('工具数:', len(create_doc_agent().tools))"
# 预期输出：工具数: 23
```

---

## 六、配置说明

配置文件位于 [config.py](config.py)，使用 `pydantic-settings` 管理，支持通过环境变量或 `.env` 文件覆盖。

### 6.1 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `model` | `sensenova-6.8-flash-lite` | LLM 模型名称 |
| `base_url` | `https://token.sensenova.cn/v1` | LLM API 地址 |
| `api_key` | （内置） | API 密钥 |
| `agent_max_iterations` | `10` | Agent 最大迭代次数 |

### 6.2 使用 .env 文件覆盖

在项目根目录创建 `.env` 文件：

```env
MODEL=your-model-name
BASE_URL=https://your-api-endpoint/v1
API_KEY=your-api-key
```

> **注意**：配置项不区分大小写，环境变量名需大写。

---

## 七、快速开始

### 7.1 运行完整演示

```bash
python langchainmain.py
```

程序会依次演示三条执行通道：
1. **LCEL 简单问答链**：单轮问答
2. **通用工具 Agent**：天气查询、计算器
3. **文档办公助手**：读取 docx → 润色 → 生成新 docx

### 7.2 使用文档办公助手

```python
from agent.doc_agent import create_doc_agent

agent = create_doc_agent()

# 润色论文
agent.run("读取 D:/论文/初稿.docx，进行学术润色，保存为 D:/论文/润色版.docx")

# 总结文档
agent.run("帮我总结 D:/报告/季度汇报.docx，控制在 300 字以内")

# 翻译文档
agent.run("把 D:/合同/agreement.docx 翻译成中文，保存到 D:/合同/中文版.docx")

# 构建知识库并问答
agent.run("把 D:/论文资料 文件夹建成知识库")
agent.run("知识库中关于深度学习的应用有哪些？")
```

### 7.3 使用通用 Agent

```python
from agent.agent import LangChainAgent
from tools import get_tools

agent = LangChainAgent(tools=get_tools())
agent.run("东京天气怎么样？")
```

---

## 八、工具详解

### 8.1 文档读写与内容处理

| 工具 | 参数 | 说明 |
|------|------|------|
| `read_document` | `file_path` | 读取本地 .docx 全文（段落+表格） |
| `write_document` | `file_path, content, title` | 将内容写入新的 .docx |
| `polish_text` | `text, style` | 润色文本，style：学术/商务/正式/口语/简洁 |
| `summarize_text` | `text, max_length` | 摘要总结，可控制字数 |
| `translate_text` | `text, target_language` | 翻译文本（中/英/日等） |
| `check_grammar` | `text` | 语法/用词/逻辑检查 + 修改建议 |

### 8.2 文档结构增强

| 工具 | 参数 | 说明 |
|------|------|------|
| `extract_outline` | `file_path` | 提取文档大纲（识别 Heading 样式） |
| `generate_toc` | `file_path` | 基于大纲生成目录文本 |
| `format_reference` | `reference, style` | 格式化参考文献（GB/T 7714/APA/MLA） |

### 8.3 表格与数据

| 工具 | 参数 | 说明 |
|------|------|------|
| `read_table` | `file_path, table_index` | 读取 docx 指定表格，输出 Markdown 表格 |
| `create_chart` | `title, labels, values, chart_type, output_path` | 生成柱状/折线/饼图 |
| `excel_summary` | `file_path, sheet_name` | 读取 Excel + LLM 生成分析报告 |

### 8.4 论文专项

| 工具 | 参数 | 说明 |
|------|------|------|
| `check_plagiarism` | `text1, text2` | n-gram 相似度查重，输出重复片段 |
| `academic_search` | `query, max_results` | 调用 arXiv API 搜索学术论文 |
| `format_paper` | `file_path, output_path` | 按学术标准排版 docx（宋体小四、1.5倍行距等） |

### 8.5 多格式支持

| 工具 | 参数 | 说明 |
|------|------|------|
| `convert_format` | `input_path, output_path` | docx → markdown / 纯文本 |
| `read_pdf` | `file_path, max_pages` | 提取 PDF 文本，支持指定页数 |

### 8.6 流程自动化

| 工具 | 参数 | 说明 |
|------|------|------|
| `batch_process` | `folder_path, operation` | 批量处理文件夹 docx（润色/总结/翻译） |
| `compare_versions` | `file_path_a, file_path_b` | 对比两个版本文档差异 |
| `email_draft` | `key_points, tone` | 根据要点生成商务邮件草稿 |

### 8.7 知识管理 RAG

| 工具 | 参数 | 说明 |
|------|------|------|
| `build_knowledge_base` | `folder_path` | 加载文件夹文档→分块→向量化→存入 Chroma |
| `search_knowledge_base` | `query, k` | 语义检索 Top-K 相关片段 |
| `extract_keywords` | `text, max_keywords` | LLM 提取文档关键词/标签 |

---

## 九、架构原理

### 9.1 三条执行通道

本框架包含三种基于 LangChain 的执行模式：

```
通道一：LCEL 数据流水线
  prompt | llm | parser
  适用于单轮问答，数据从左到右流过每个节点

通道二：LangGraph Agent（通用）
  LLM 节点 ↔ 工具节点 循环执行
  通过 messages Channel（add_messages 归约器）累积对话历史

通道三：文档办公 Agent
  基于通道二，注入 23 个文档办公专用工具
```

### 9.2 LangGraph 状态图与 Channel

Agent 基于 `langchain.agents.create_agent` 构建，内部编译为 LangGraph 的 `CompiledStateGraph`。

核心机制：
- **State**：`AgentState` 是 TypedDict，核心字段为 `messages`
- **Channel**：`messages` 字段使用 `add_messages` 归约器，节点产生的新消息会被追加而非覆盖
- **循环**：LLM 节点决定是否调用工具 → 工具节点执行 → 结果回传 LLM，直到 LLM 不再调用工具

```
        messages Channel（累积对话历史）
              │
    ┌─────────┴─────────┐
    ▼                   ▼
 LLM 节点  ◄──────►   工具节点
 (推理/决策)    循环    (执行工具)
```

### 9.3 RAG 知识库原理

```
离线建库                          在线检索
┌──────────────────┐            ┌──────────────────┐
│ 文档(docx/pdf/txt)│            │ 用户 query        │
│     ↓             │            │     ↓             │
│ 文本分块(500字符)  │            │ 向量化(embed)     │
│     ↓             │            │     ↓             │
│ 向量化(bge-small) │            │ Chroma 余弦检索    │
│     ↓             │            │     ↓             │
│ Chroma 持久化存储  │            │ 返回 Top-K 片段    │
└──────────────────┘            └──────────────────┘
                                      ↓
                              LLM 基于片段生成答案
```

关键技术点：
- **Embedding 模型**：`BAAI/bge-small-zh-v1.5`（中文专用，512 维，无需 torch）
- **向量库**：Chroma 本地持久化，HNSW 索引 + 余弦相似度
- **分块策略**：500 字符/块，重叠 50 字符，递归分割（优先段落→行→句号）
- **去重机制**：基于内容 MD5 生成 ID，重复内容不重复入库

---

## 十、常见问题

### Q1：首次运行很慢？

首次使用 RAG 功能时，fastembed 会自动下载 `bge-small-zh-v1.5` 模型（约 90MB），仅需下载一次，后续使用本地缓存。

### Q2：如何更换 LLM 模型？

修改 `config.py` 中的 `model`、`base_url`、`api_key`，或通过环境变量/`.env` 文件覆盖。

### Q3：知识库数据存在哪里？

默认存储在项目根目录的 `chroma_db/` 文件夹中，可通过 `VectorStore(persist_dir=...)` 自定义路径。

### Q4：如何清空知识库？

```python
from core.vectorstore import get_vector_store
get_vector_store().clear()
```

### Q5：支持哪些文档格式？

- **读取**：.docx、.pdf、.txt、.md
- **生成**：.docx、.md、.txt、.png（图表）

### Q6：查重工具的准确率如何？

`check_plagiarism` 基于字符 n-gram 重叠率计算，适合快速对比两段文本的相似度。如需正式查重，请接入专业查重系统（如知网、万方）。

### Q7：如何新增自定义工具？

1. 在 `tools/` 目录下新建 `.py` 文件
2. 使用 `@tool` 装饰器定义函数
3. 在 `agent/doc_agent.py` 中导入并加入 `doc_tools` 列表
4. 工具会自动被发现并注册

### Q8：Agent 最多能调用多少次工具？

由 `config.py` 中的 `agent_max_iterations` 控制，默认 10 次，防止无限循环。

---

## 附录：运行示例输出

```
🚀 LangChain Agent Framework 启动

============================================================
通道三：文档办公助手 (读 docx → 润色 → 写 docx)
============================================================
📄 已创建样例文档：D:\fxy\agentframework\output\论文草稿.docx

🤖 助手回复：
润色版文档已成功保存至 D:\fxy\agentframework\output\论文润色版.docx。

## 润色前后对比要点
| 维度 | 润色前 | 润色后 |
|------|--------|--------|
| 用词正式度 | "发展很快" | "呈现出迅猛的发展态势" |
| ...
```
