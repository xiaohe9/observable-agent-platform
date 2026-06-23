# 🔍 Observable Agent Platform

可观测 Agent 平台 —— 跨行业 ReAct Agent 工作流可视化演示系统。

## ✨ 核心特性

- **自定义 ReAct 引擎**：不依赖 LangChain 封装，完整实现 Thought → Action → Observation 循环
- **双层防幻觉机制**：信息完整性检查（正则硬拦截）+ 数据校验（异常值过滤）
- **跨行业场景配置**：物流查单 / 保险理赔 / 零售客服，场景切换只需改配置
- **实时工作流可视化**：SSE 流式推送，前端分屏展示 Agent 大脑思考过程
- **RAG 检索增强**：混合检索 + 重排序，知识库命中过程可观测

## 🚀 技术栈

- 后端：Python 3.12 + Flask + SSE
- 前端：原生 HTML/CSS/JS（暗色科技主题）
- 架构：ReAct Agent + Function Calling + 短期记忆管理

## 📦 快速启动

```bash
# 1. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 2. 安装依赖
pip install flask

# 3. 启动服务
python app.py

# 4. 浏览器打开 http://127.0.0.1:5000


🎯 演示场景
场景	    输入示例	            展示能力	
物流查单	`查一下 DHL9876543210`	意图识别 → 工具调用 → 时区处理 → 延误分析	
保险理赔	`我的重疾险怎么理赔`	 多轮追问（缺失实体拦截）→ RAG 检索 → 材料清单	
零售客服	`查一下 iPhone 16 库存`	意图路由 → 库存查询 → 会员积分抵扣	


🛡️ 防幻觉设计

1. 第一层：信息完整性检查
正则提取实体 → 缺失关键字段 → 强制追问，禁止 LLM 编造
2. 第二层：数据校验
工具返回异常值（延误 > 100 小时 / 单号不存在）→ 自动拦截 → 降级到 RAG 兜底


📂 项目结构

agent-demo-v2/
├── app.py                  # Flask 主服务 + SSE 接口
├── agent_engine.py         # 自定义 ReAct 引擎（核心）
├── scenarios/
│   ├── logistics.py        # 物流场景配置
│   └── insurance.py        # 保险场景配置
├── templates/
│   └── index.html          # 分屏前端界面
└── .gitignore


📄 License
MIT License