# RAG 方法对比与来源说明

日期：2026-06-04

## 1. 背景

本文件用于整理 PageIndex 与其他 RAG 方法的对比对象、官方来源、适用场景和推荐评估路线。

核心问题不是：

> PageIndex 是否全面优于所有 RAG？

而是：

> 在结构化长文档中，PageIndex 是否能更稳定地找到正确证据、给出页码引用，并提供可解释的检索路径？

重点场景包括：

- SEC filings / 年报
- 合同
- 法规
- 技术手册
- 审计类文档

## 2. 对比对象总览

| 方法 | 主要能力 | 适合场景 | 官方来源 |
|---|---|---|---|
| PageIndex | 基于文档树结构的推理检索 | 长文档、章节定位、页码引用 | https://github.com/VectifyAI/PageIndex |
| Long-context LLM | 直接把全文放入上下文 | 小规模文档、强 baseline | https://platform.openai.com/docs/api-reference/responses/create |
| Vector RAG + reranker | 向量检索后用 reranker 重排 | 通用语义检索 | https://github.com/run-llama/llama_index |
| GraphRAG | 实体关系图、社区摘要、全局/局部搜索 | 跨文档关系分析、主题归纳 | https://github.com/microsoft/graphrag |
| Hybrid RAG | BM25 + 向量检索融合 | 强通用 baseline | https://docs.llamaindex.ai/ |
| HyperGraphRAG | 高阶关系、n-ary facts、多跳推理 | 多实体复杂关系推理 | https://github.com/LHRLAB/HyperGraphRAG |

## 3. PageIndex

PageIndex 的核心思路是：

```text
document -> tree index -> reasoning-based retrieval -> answer
```

它把长文档转成类似目录树的结构，节点包含章节、页码范围、摘要等信息。查询时，模型不是只找相似 chunk，而是沿着文档结构进行推理式检索。

适合验证：

- 章节定位能力
- 页码级 evidence recall
- citation precision
- 检索路径可解释性
- 长文档结构理解能力

来源：

- GitHub: https://github.com/VectifyAI/PageIndex
- Docs: https://docs.pageindex.ai/
- Website: https://pageindex.ai/

## 4. Long-context LLM

Long-context LLM 不是 RAG 框架，而是 baseline。做法是把整份文档文本直接放入上下文，让模型回答并引用页码。

它用于回答一个关键问题：

> 如果模型已经能直接读全文，PageIndex 是否仍然有价值？

需要比较：

- 答案准确率
- 引用是否正确
- token 成本
- 延迟
- 长文档下是否遗漏关键信息

来源：

- OpenAI Responses API: https://platform.openai.com/docs/api-reference/responses/create
- Gemini Long Context: https://ai.google.dev/gemini-api/docs/long-context

## 5. Vector RAG + Reranker

传统强 baseline：

```text
document -> chunks -> embeddings -> vector search -> reranker -> answer
```

建议使用 LlamaIndex 快速实现，并使用 sentence-transformers 或其他 reranker 做重排。

适合验证：

- 传统 RAG 在相似度检索上的表现
- reranker 是否能弥补 chunk 检索不足
- PageIndex 是否真的比强 vector baseline 更好

来源：

- LlamaIndex GitHub: https://github.com/run-llama/llama_index
- LlamaIndex Docs: https://docs.llamaindex.ai/
- Reranker docs: https://docs.llamaindex.ai/en/v0.10.34/module_guides/querying/node_postprocessors/node_postprocessors/
- FAISS: https://github.com/facebookresearch/faiss

## 6. GraphRAG

GraphRAG 的核心思路是：

```text
documents -> entities / relationships / claims -> graph -> community summaries -> graph search -> answer
```

它适合跨文档分析、实体关系、主题聚合和全局问题，不一定专门适合单文档页码级引用。

适合验证：

- 跨文档关系检索
- 实体关系推理
- 主题归纳
- 多文档全局问题

来源：

- GitHub: https://github.com/microsoft/graphrag
- Docs: https://microsoft.github.io/graphrag/
- Quickstart: https://microsoft.github.io/graphrag/get_started/

## 7. Hybrid RAG

Hybrid RAG 不是单一项目，而是一类方法。推荐第一版使用 LlamaIndex 实现：

```text
BM25 keyword retrieval + vector retrieval + fusion/rerank -> answer
```

它通常是比单纯 Vector RAG 更强的 baseline，因为它同时利用关键词匹配和语义相似度。

适合验证：

- keyword search 与 vector search 的互补性
- PageIndex 是否能超过强混合检索 baseline
- 精确术语、财务指标、合同条款的命中能力

来源：

- LlamaIndex BM25 Retriever: https://docs.llamaindex.ai/en/latest/examples/retrievers/bm25_retriever/
- Reciprocal Rerank Fusion: https://docs.llamaindex.ai/en/v0.10.34/examples/retrievers/reciprocal_rerank_fusion/
- Qdrant Hybrid Search: https://qdrant.tech/documentation/search/hybrid-queries/

## 8. HyperGraphRAG

HyperGraphRAG 关注高阶关系，不只是普通图里的二元关系。

普通 GraphRAG 常见关系：

```text
A --relation--> B
```

HyperGraphRAG 更强调：

```text
relation(A, B, C, D...)
```

因此它适合 n-ary facts、多实体关系、多跳推理。

适合验证：

- 多实体复杂关系
- 高阶事实检索
- multi-hop QA
- 普通 GraphRAG 难以表达的复杂关系

来源：

- HyperGraphRAG GitHub: https://github.com/LHRLAB/HyperGraphRAG
- Paper: https://arxiv.org/abs/2503.21322
- NeurIPS 2025: https://proceedings.neurips.cc/paper_files/paper/2025/hash/df55ee6e59f8ac4a625219e11fe9ddba-Abstract-Conference.html
- 相关项目 Hyper-RAG: https://github.com/iMoonLab/Hyper-RAG

## 9. 推荐数据集

### 第一阶段：金融文档

推荐使用 FinanceBench。

来源：

- GitHub: https://github.com/patronus-ai/financebench
- Paper: https://arxiv.org/abs/2311.11944

原因：

- 基于真实 SEC filings
- 包含 gold answer
- 包含 evidence page
- 非常适合评估 citation precision 和 evidence recall
- 与 PageIndex 的长文档结构检索定位匹配

适合问题类型：

- 财务指标提取
- 表格定位
- 年报章节定位
- MD&A 与财务附注交叉验证
- 风险因素定位

### 第二阶段：法律合同

推荐使用 CUAD。

来源：

- GitHub: https://github.com/TheAtticusProject/cuad
- Paper: https://arxiv.org/abs/2103.06268

原因：

- 合同结构清晰
- 条款定位明确
- 适合 clause retrieval
- 适合 evidence extraction

注意：CUAD 更偏条款抽取，不是天然问答数据集，需要额外构造成 QA benchmark。

## 10. 评估指标

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

其中最重要的是：

```text
evidence_recall
citation_precision
```

因为 PageIndex 的核心优势如果存在，应主要体现在：

- 是否找到正确证据页
- 引用是否真的支持答案
- 检索路径是否可解释

## 11. 推荐实施顺序

第一阶段：

```text
PageIndex
Long-context LLM
Vector RAG + reranker
Hybrid RAG
FinanceBench
```

第二阶段：

```text
GraphRAG
CUAD
跨文档问题
```

第三阶段：

```text
HyperGraphRAG
多实体关系问题
multi-hop QA
n-ary fact retrieval
```

## 12. 结论边界

合理的结论不应该是“某个方法全面最好”，而应该是：

```text
PageIndex 更适合结构化长文档、章节定位、页码证据和可解释检索。
Vector RAG + reranker 更通用，成本更低。
Hybrid RAG 是很强的传统 baseline。
GraphRAG 更适合跨文档实体关系和主题归纳。
HyperGraphRAG 更适合高阶关系和多跳推理。
Long-context LLM 是必须对比的强 baseline，但需要评估成本、延迟和长文档稳定性。
```

## 13. 推荐路线

如果目标是验证 PageIndex 的独特优势，第一版不建议从医学书籍开始。更合理的路线是：

```text
FinanceBench / SEC filings -> CUAD contracts -> GraphRAG / HyperGraphRAG multi-hop comparison
```

第一版应优先证明：

> 在金融年报这类结构化长文档中，PageIndex 是否能比 Long-context LLM、Vector RAG + reranker 和 Hybrid RAG 更准确地定位证据、引用页码，并提供更清晰的检索路径。
