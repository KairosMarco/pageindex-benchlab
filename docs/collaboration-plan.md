# PageIndex BenchLab 协作与贡献计划

日期：2026-06-04

## 1. 项目目标

我们计划共同完成一个开源项目：**PageIndex BenchLab**。

这个项目的目标是系统对比不同 RAG 方法在结构化长文档问答中的表现，尤其关注 PageIndex 是否能在以下方面体现独特优势：

- 找到正确证据页
- 给出可靠引用
- 保留章节和文档结构
- 展示可解释的检索路径
- 在成本和延迟上相比 Long-context LLM 更可控

核心问题不是：

> PageIndex 是否全面优于所有 RAG？

而是：

> 在 SEC filings、年报、合同等结构化长文档中，PageIndex 是否能比 Long-context LLM、Vector RAG + reranker、Hybrid RAG、GraphRAG、HyperGraphRAG 更稳定地定位证据并回答问题？

## 2. 预期产出

第一阶段目标不是做一个普通 demo，而是做一个可复现的 benchmark 项目。

预期产出包括：

- 一个公开 GitHub 仓库
- 一套可运行的 RAG pipeline 对比代码
- 一批基于 FinanceBench / SEC filings 的测试问题
- 统一的输出 schema
- evidence recall / citation precision 等评估指标
- Markdown / HTML / DOCX 格式报告
- 可以反向贡献给 PageIndex、LlamaIndex、GraphRAG 等项目的 PR

## 3. 协作流程图

![PageIndex BenchLab 协作与贡献流程](pageindex-rag-workflow.png)

## 4. 角色分工

### 你的职责

你负责项目方向、评测定义、文档和社区沟通，同时尝试实现第一版 MVP。

具体包括：

- 定义问题集
- 定义评估指标
- 设计报告结构
- 编写 README
- 制定贡献路线
- 与 PageIndex、LlamaIndex、GraphRAG 等社区沟通
- 尝试实现第一版要求
- 维护项目目标、结论边界和可复现性

你更偏向：

```text
benchmark design
documentation
evaluation protocol
open-source roadmap
community communication
MVP coordination
```

### PH 的职责

PH 负责主要工程接入、实验运行和代码实现。

具体包括：

- 接入 PageIndex
- 接入 LlamaIndex
- 接入 GraphRAG
- 接入 HyperGraphRAG
- 实现 pipeline adapter
- 跑实验
- 写代码
- 记录运行环境、模型版本、token 使用量、延迟和失败案例

PH 更偏向：

```text
RAG pipeline implementation
adapter development
experiment execution
benchmark automation
code quality
failure analysis
```

## 5. 对比方法与来源

| 方法 | 主要能力 | 适合场景 | 来源 |
|---|---|---|---|
| PageIndex | 基于文档树结构的推理检索 | 长文档、章节定位、页码引用 | https://github.com/VectifyAI/PageIndex |
| Long-context LLM | 直接把全文放入上下文 | 小规模文档、强 baseline | https://platform.openai.com/docs/api-reference/responses/create |
| Vector RAG + reranker | 向量检索后用 reranker 重排 | 通用语义检索 | https://github.com/run-llama/llama_index |
| Hybrid RAG | BM25 + 向量检索融合 | 强通用 baseline | https://docs.llamaindex.ai/ |
| GraphRAG | 实体关系图、社区摘要、全局/局部搜索 | 跨文档关系分析、主题归纳 | https://github.com/microsoft/graphrag |
| HyperGraphRAG | 高阶关系、n-ary facts、多跳推理 | 多实体复杂关系推理 | https://github.com/LHRLAB/HyperGraphRAG |

相关来源：

- PageIndex Docs: https://docs.pageindex.ai/
- LlamaIndex Docs: https://docs.llamaindex.ai/
- LlamaIndex GitHub: https://github.com/run-llama/llama_index
- Microsoft GraphRAG Docs: https://microsoft.github.io/graphrag/
- Microsoft GraphRAG GitHub: https://github.com/microsoft/graphrag
- HyperGraphRAG Paper: https://arxiv.org/abs/2503.21322
- Hyper-RAG 相关项目: https://github.com/iMoonLab/Hyper-RAG
- Qdrant Hybrid Search: https://qdrant.tech/documentation/search/hybrid-queries/
- FAISS: https://github.com/facebookresearch/faiss

## 6. 方法定位

### PageIndex

PageIndex 的核心流程：

```text
document -> tree index -> reasoning-based retrieval -> answer
```

它更适合结构化长文档、章节定位、页码证据和可解释检索。

### Long-context LLM

Long-context LLM 不是 RAG 框架，而是强 baseline。

流程：

```text
document full text -> long context prompt -> answer
```

它用于验证一个问题：

> 如果模型已经能直接读全文，PageIndex 是否仍然有价值？

### Vector RAG + Reranker

传统强 baseline：

```text
document -> chunks -> embeddings -> top-k retrieval -> reranker -> answer
```

它适合测试 PageIndex 是否真的优于常规强 RAG pipeline。

### Hybrid RAG

Hybrid RAG 通常结合关键词检索和向量检索：

```text
BM25 keyword search + vector search + fusion/rerank -> answer
```

它通常比单纯 Vector RAG 更稳，是第一阶段非常重要的 baseline。

### GraphRAG

GraphRAG 的核心流程：

```text
documents -> entities / relationships / claims -> graph -> community summaries -> graph search -> answer
```

它更适合跨文档实体关系、主题归纳和全局问题。

### HyperGraphRAG

HyperGraphRAG 更关注高阶关系和 n-ary facts：

```text
relation(A, B, C, D...)
```

它适合多实体复杂关系、多跳推理和普通二元图难以表达的问题。

## 7. 数据集选择

第一阶段推荐使用金融文档，不建议直接从医学书籍开始。

原因：

- 医学书籍版权复杂
- 医学答案需要专业审查
- 容易变成模型医学知识测试，而不是文档检索测试
- 高风险领域需要更严格免责声明和验证流程

### 第一阶段：FinanceBench / SEC filings

来源：

- FinanceBench GitHub: https://github.com/patronus-ai/financebench
- FinanceBench Paper: https://arxiv.org/abs/2311.11944

适合原因：

- 基于真实 SEC filings
- 包含 gold answer
- 包含 evidence page
- 适合评估 evidence recall 和 citation precision
- 与 PageIndex 的长文档结构检索定位匹配

### 第二阶段：CUAD 合同

来源：

- CUAD GitHub: https://github.com/TheAtticusProject/cuad
- CUAD Paper: https://arxiv.org/abs/2103.06268

适合原因：

- 合同结构清晰
- 条款定位明确
- 适合 clause retrieval 和 evidence extraction

## 8. 评估指标

建议统一记录以下指标：

```text
answer_accuracy
evidence_recall
citation_precision
unsupported_claim_rate
retrieval_explainability
token_cost
latency
indexing_cost
```

第一阶段最重要的是：

```text
evidence_recall
citation_precision
```

因为 PageIndex 的优势如果成立，应该主要体现在：

- 是否找到真正支持答案的页面或章节
- 引用是否确实支持答案
- 检索路径是否可解释

## 9. 第一版 MVP 范围

第一版不要一开始接入所有方法。建议先做：

```text
PageIndex
Long-context LLM
Vector RAG + reranker
Hybrid RAG
FinanceBench 10-20 个问题
```

第一版交付目标：

- 能跑 10-20 个 FinanceBench 问题
- 每个方法输出统一 JSON
- 每个回答包含 answer、citations、retrieval_trace、token_usage、latency
- 能计算 evidence recall
- 能计算 citation precision
- 能生成 Markdown / HTML 报告

建议统一输出 schema：

```json
{
  "method": "pageindex",
  "question_id": "q001",
  "question": "...",
  "answer": "...",
  "citations": [
    {
      "document_id": "apple_2023_10k",
      "page": 42,
      "section": "Item 7",
      "text": "..."
    }
  ],
  "retrieval_trace": [
    {
      "step": 1,
      "action": "inspect_tree",
      "target": "Item 7"
    }
  ],
  "token_usage": {
    "input": 12000,
    "output": 800
  },
  "latency_ms": 8400
}
```

## 10. GitHub 贡献路线

PR 是 Pull Request，即向上游开源项目提交修改，请维护者合并。

成为 contributor 不能保证，关键取决于 PR 是否被维护者合并。

最现实的路线是先做小 PR：

- 文档修复
- Windows quickstart
- `.env.example`
- 示例修复
- README 补充
- benchmark 复现说明
- 小型 eval script

不要一开始提交大功能。每个 PR 只解决一个问题。

### PageIndex 贡献建议

优先尝试：

- 跑通官方 demo
- 记录 Windows 环境问题
- 补充 Windows quickstart
- 增加 FinanceBench 复现实验说明
- 增加最小 PDF 示例
- 改进错误提示或文档说明

### LlamaIndex 贡献建议

优先尝试：

- 补充长文档 Vector RAG + reranker 示例
- 补充 Hybrid RAG benchmark example
- 修复文档或示例问题

### GraphRAG 贡献建议

优先尝试：

- 先阅读 CONTRIBUTING.md
- 先开 issue 说明 benchmark 接入计划
- 注意 Microsoft CLA
- 提交小型文档或示例 PR

来源：

- GraphRAG CONTRIBUTING: https://github.com/microsoft/graphrag/blob/main/CONTRIBUTING.md

## 11. 四周执行计划

### 第 1 周

- 建立 GitHub 仓库
- 放入本项目文档
- PH 跑通 PageIndex
- 你整理 FinanceBench 问题子集
- 定义统一输出 schema
- 开始 README

### 第 2 周

- PH 实现 PageIndex adapter
- PH 实现 Vector RAG + reranker baseline
- 你定义 evidence recall 和 citation precision
- 你完成第一版报告模板
- 双方跑通 10 个问题

### 第 3 周

- PH 实现 Hybrid RAG baseline
- 你实现或协助实现 Long-context baseline
- 输出第一版 benchmark report
- 整理失败案例
- 向 PageIndex 开 issue，说明 benchmark 计划

### 第 4 周

- 发布 v0.1
- 提交第一个 PageIndex 小 PR
- 完善 README
- 写一篇技术总结
- 规划 GraphRAG / HyperGraphRAG 第二阶段接入

## 12. 是否需要显卡

第一阶段不需要显卡。

不需要显卡的任务：

- 写文档
- 修 README
- 提交 PR
- 调 OpenAI / Gemini / Claude API
- 跑 PageIndex 基础 demo
- 做 Long-context baseline
- 小规模 Vector RAG / Hybrid RAG
- 小规模 GraphRAG 实验

可能需要显卡的情况：

- 本地跑开源大模型
- 本地大规模 embedding
- 本地跑大型 reranker
- 批量处理大量 PDF 和大规模问题集

第一阶段建议：

```text
LLM 使用 API
embedding 使用 API 或轻量模型
reranker 使用轻量模型
数据集先用 10-20 个问题
```

## 13. 协作规则

建议从第一天开始遵守：

- 所有任务必须开 GitHub issue
- 每个 PR 只解决一个问题
- 每个实验必须记录模型、prompt、版本、token、延迟
- 不做无法复现的宣传性结论
- 不直接声称 PageIndex 全面优于其他方法
- 所有 benchmark 结果必须保留原始输出
- 所有结论必须能从实验数据中追溯

## 14. 最终定位

这个项目的定位应该是：

> PageIndex BenchLab 是一个面向结构化长文档问答的开源 RAG 评测工作台，用于对比 PageIndex、Long-context LLM、Vector RAG + reranker、Hybrid RAG、GraphRAG 和 HyperGraphRAG 在 evidence recall、citation precision、answer accuracy、token cost、latency 和 retrieval explainability 上的表现。

合理的预期结论不是“某个方法全面最好”，而是：

```text
PageIndex 更适合结构化单文档问答、章节定位和页码级引用。
Vector RAG + reranker 更通用，成本更低。
Hybrid RAG 是很强的传统 baseline。
GraphRAG 更适合跨文档实体关系和主题归纳。
HyperGraphRAG 更适合高阶关系和多跳推理。
Long-context LLM 是必须对比的强 baseline，但需要评估成本、延迟和长文档稳定性。
```

## 15. 下一步行动

建议立刻执行：

1. 创建 GitHub 仓库：`pageindex-benchlab`
2. 上传本文档和流程图
3. 确认 PH 是否接受当前分工
4. 选择 10-20 个 FinanceBench 问题作为第一批样本
5. 跑通 PageIndex 本地 demo
6. 实现统一输出 schema
7. 在 PageIndex 仓库开第一个 issue 或小 PR
