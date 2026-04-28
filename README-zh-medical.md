# EvoAgentX 医疗AI增强版

<div align="center">

**自进化医疗研究Agent框架** · PubMed · 临床试验 · FDA药物 · 进化引擎

[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat-square&logo=python)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat-square&logo=docker)]()
[![Tests](https://img.shields.io/badge/Tests-30%2F30-10b981.svg?style=flat-square)]()

</div>

---

## 这是什么？

EvoAgentX医疗AI是一个**开源、自进化的Agent框架**，专为医学研究设计。它直连4大医学数据库，运行自动化研究管线，并通过3层进化引擎持续自我优化。

**一条命令。真实数据。自动进化。**

```bash
python examples/medical/end_to_end_demo.py --topic "CRISPR基因治疗"
# → 搜索4个数据库，18秒生成完整报告
```

## 核心能力

| 能力 | 说明 | 数据源 |
|------|------|--------|
| 文献检索 | PubMed 3900万+篇文献，支持MeSH词表 | NCBI E-utilities |
| 临床试验 | 50万+项临床试验，按阶段/状态筛选 | ClinicalTrials.gov |
| 药物信息 | FDA药品标签、适应症、不良反应 | OpenFDA |
| 药物交互 | 基于FAERS的药物相互作用分析 | FDA FAERS |
| 药物标准化 | 药名规范化、成分查询 | NLM RxNorm |
| 自进化 | 3层进化引擎持续优化Agent | Darwin+EvoPrompt+SEW |
| 评估基准 | 15道医学题目覆盖临床/药物/推理 | 内置 |

## 快速开始

### 方式一：Python

```bash
git clone https://github.com/MoKangMedical/EvoAgentX.git
cd EvoAgentX
python -m venv venv && source venv/bin/activate
pip install -e ".[tools]" -i https://pypi.tuna.tsinghua.edu.cn/simple

# 验证安装
python evoagentx/setup_wizard.py

# 运行完整管线（不需要API Key）
python examples/medical/end_to_end_demo.py
```

### 方式二：Docker

```bash
docker build -t evoagentx .
docker run --rm evoagentx status
docker run -p 8000:8000 evoagentx
```

### 方式三：Makefile

```bash
make setup       # 安装 + 验证
make demo-e2e    # 端到端管线
make test-med    # 30个测试
make serve       # 启动API服务
```

## CLI命令

```bash
evoagentx setup                    # 首次配置向导
evoagentx status                   # 系统状态（API连通性 + 项目检测）
evoagentx search "基因治疗"         # PubMed搜索
evoagentx drugs pembrolizumab      # FDA药物查询
evoagentx drugs --interaction a,b  # 药物交互检查
evoagentx trials "CAR-T"           # 临床试验搜索
evoagentx demo [medical|evox|all]  # 运行演示
evoagentx serve --port 8000        # 启动API服务
evoagentx test --medical-only      # 运行测试
evoagentx evolve --rounds 5        # 运行进化
```

## 架构

```
┌─────────────────────────────────────────────────────┐
│              EvoAgentX 医疗AI                        │
├─────────────────────────────────────────────────────┤
│  ┌────────┐ ┌──────────┐ ┌───────┐ ┌────────────┐  │
│  │ PubMed │ │临床试验   │ │OpenFDA│ │   RxNorm   │  │
│  └───┬────┘ └────┬─────┘ └───┬───┘ └─────┬──────┘  │
│      └───────────┴───────────┴───────────┘          │
│                    ↓                                 │
│  ┌───────────────────────────────────────────────┐  │
│  │  医学工具层 (7个工具) + 缓存 + 限速 + 健康检查 │  │
│  └───────────────────┬───────────────────────────┘  │
│                      ↓                               │
│  ┌───────────────────────────────────────────────┐  │
│  │  工作流引擎 (文献综述 / 药物安全 / 自定义)     │  │
│  └───────────────────┬───────────────────────────┘  │
│                      ↓                               │
│  ┌───────────────────────────────────────────────┐  │
│  │  EvoX进化桥接 (Darwin + EvoPrompt + SEW)      │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────┐ ┌───────┐ ┌─────────┐ ┌───────────────┐  │
│  │ CLI  │ │REST API│ │Dashboard│ │医学评估基准    │  │
│  └──────┘ └───────┘ └─────────┘ └───────────────┘  │
└─────────────────────────────────────────────────────┘
```

## OPC项目集成

| 项目 | 集成方式 | 用途 |
|------|---------|------|
| [MetaForge](https://github.com/MoKangMedical/metaforge) | PubMed管线 | 系统综述 |
| [DrugMind](https://github.com/MoKangMedical/drugmind) | 药物工具 | 药物研发 |
| [PharmaSim](https://github.com/MoKangMedical/PharmaSim) | 试验数据 | 市场仿真 |
| [MediChat-RD](https://github.com/MoKangMedical/medichat-rd) | 桥接模块 | 罕见病 |
| [EvoX](https://github.com/MoKangMedical/evox) | 进化引擎 | 3层优化 |
| [KnowHealth](https://github.com/MoKangMedical/KnowHealth) | HITL | 多医生审核 |

## 测试

```bash
make test-med
# 30/30 通过 (42秒)
# ├── PubMed: 5个测试
# ├── 临床试验: 5个测试
# ├── 药物: 7个测试
# ├── 注册表: 4个测试
# └── 桥接: 4个测试
```

## 许可证

MIT License — 详见 [LICENSE](LICENSE)

基于 [EvoAgentX](https://github.com/EvoAgentX/EvoAgentX) by EvoAgentX Team。
医疗AI增强 by [MoKangMedical](https://github.com/MoKangMedical)。
