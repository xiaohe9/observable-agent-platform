"""
自定义 ReAct Agent 引擎（不依赖 LangChain）
支持 SSE 流式推送、双层防幻觉、Mock LLM 推理
"""

import json
import time
from typing import Generator, Optional

import scenarios.logistics as logistics
import scenarios.insurance as insurance

# 场景注册表
SCENARIOS = {
    "logistics": logistics,
    "insurance": insurance,
}


class ReActEngine:
    """ReAct 推理引擎：Thought → Action → Observation → Final Answer"""

    def __init__(self, scenario_id: str, session_entities: Optional[dict] = None):
        """
        初始化引擎
        scenario_id: 场景标识（logistics / insurance）
        session_entities: 跨轮次累积的实体（用于多轮追问）
        """
        self.scenario_id = scenario_id
        self.scenario = SCENARIOS.get(scenario_id, logistics)
        self.session_entities = session_entities or {}

    def run(self, user_message: str) -> Generator[str, None, None]:
        """
        执行完整 ReAct 流程，逐步 yield SSE 事件
        每个事件格式：data: {json}\n\n
        """
        # ── Step 1: 意图识别 ──
        intent = self.scenario.detect_intent(user_message)
        yield self._emit(
            "intent",
            {
                "intent": intent,
                "label": self.scenario.get_intent_label(intent),
                "confidence": 0.92,
                "message": f"识别到用户意图：{self.scenario.get_intent_label(intent)}",
            },
        )
        time.sleep(0.4)

        # ── Step 2: 实体提取 + 合并会话上下文 ──
        new_entities = self.scenario.extract_entities(user_message)
        self.session_entities.update(new_entities)

        yield self._emit(
            "thought",
            {
                "content": f"正在分析用户输入，已提取实体：{self._format_entities(self.session_entities) or '暂无'}",
                "step": 1,
            },
        )
        time.sleep(0.5)

        # ── 第一层防幻觉：信息完整性检查 ──
        required = self.scenario.INTENT_REQUIRED_ENTITIES.get(intent, [])
        missing = [e for e in required if e not in self.session_entities]

        if missing:
            followup_parts = [
                self.scenario.FOLLOWUP_TEMPLATES.get(e, f"请提供 {e}")
                for e in missing
            ]
            followup_msg = "\n".join(followup_parts)

            yield self._emit(
                "hallucination_guard",
                {
                    "layer": 1,
                    "layer_name": "信息完整性检查",
                    "status": "intercepted",
                    "missing_entities": missing,
                    "message": f"检测到缺失关键信息：{', '.join(missing)}，已拦截并发起追问",
                    "detail": f"正则提取未能匹配到必填实体 {missing}，防止 Agent 凭空编造数据",
                },
            )
            time.sleep(0.4)

            yield self._emit(
                "final_answer",
                {
                    "content": followup_msg,
                    "is_followup": True,
                },
            )
            yield self._emit(
                "complete",
                {"session_entities": self.session_entities},
            )
            return

        yield self._emit(
            "hallucination_guard",
            {
                "layer": 1,
                "layer_name": "信息完整性检查",
                "status": "passed",
                "message": "所有必填实体已齐全，通过完整性校验",
                "entities": self.session_entities,
            },
        )
        time.sleep(0.3)

        # ── Step 3: RAG 检索 ──
        rag_docs = self.scenario.RAG_KNOWLEDGE.get(intent, [])
        yield self._emit(
            "rag",
            {
                "query": user_message,
                "documents": rag_docs,
                "count": len(rag_docs),
                "message": f"从知识库检索到 {len(rag_docs)} 条相关文档",
            },
        )
        time.sleep(0.5)

        # ── Step 4: ReAct Thought ──
        tool_name = self.scenario.get_tool_for_intent(intent)
        tools = self.scenario.get_tools()
        tool_info = tools.get(tool_name, {})

        yield self._emit(
            "thought",
            {
                "content": (
                    f"用户意图明确，实体信息完整。"
                    f"我需要调用 {tool_info.get('label', tool_name)} 工具来获取准确数据，"
                    f"而不是凭空生成答案。"
                ),
                "step": 2,
            },
        )
        time.sleep(0.6)

        # ── Step 5: Action ──
        action_params = {
            k: self.session_entities[k]
            for k in tool_info.get("params", [])
            if k in self.session_entities
        }

        yield self._emit(
            "action",
            {
                "tool": tool_name,
                "tool_label": tool_info.get("label", tool_name),
                "params": action_params,
                "message": f"Action: {tool_name}({json.dumps(action_params, ensure_ascii=False)})",
            },
        )
        time.sleep(0.5)

        # ── Step 6: Observation（工具执行） ──
        tool_result = self.scenario.execute_tool(tool_name, action_params)

        yield self._emit(
            "observation",
            {
                "tool": tool_name,
                "result": tool_result,
                "success": tool_result.get("success", False),
                "message": "工具返回结果" if tool_result.get("success") else "工具返回异常",
            },
        )
        time.sleep(0.4)

        # ── 第二层防幻觉：数据校验 ──
        if not tool_result.get("success") or tool_result.get("validation_error"):
            yield self._emit(
                "hallucination_guard",
                {
                    "layer": 2,
                    "layer_name": "数据校验",
                    "status": "intercepted",
                    "message": "工具返回异常数据，已拦截以防止幻觉输出",
                    "detail": tool_result.get("error", "数据校验失败"),
                },
            )
            time.sleep(0.3)

            yield self._emit(
                "final_answer",
                {
                    "content": tool_result.get("error", "数据校验失败，请核实您的信息后重试。"),
                    "is_error": True,
                },
            )
        else:
            yield self._emit(
                "hallucination_guard",
                {
                    "layer": 2,
                    "layer_name": "数据校验",
                    "status": "passed",
                    "message": "工具返回数据校验通过，可安全生成回复",
                },
            )
            time.sleep(0.3)

            # ── Step 7: Final Thought + Answer ──
            yield self._emit(
                "thought",
                {
                    "content": "工具返回有效数据，基于 Observation 生成最终回复，不添加任何未验证的信息。",
                    "step": 3,
                },
            )
            time.sleep(0.4)

            answer = self.scenario.format_final_answer(
                intent, tool_result, self.session_entities
            )
            yield self._emit(
                "final_answer",
                {
                    "content": answer,
                    "is_followup": False,
                },
            )

        yield self._emit(
            "complete",
            {"session_entities": self.session_entities},
        )

    def _emit(self, event_type: str, data: dict) -> str:
        """构造 SSE 事件字符串"""
        payload = {"type": event_type, **data}
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    def _format_entities(self, entities: dict) -> str:
        """格式化实体字典为可读字符串"""
        if not entities:
            return ""
        return ", ".join(f"{k}={v}" for k, v in entities.items())


def get_scenario_list() -> list:
    """获取所有可用场景列表"""
    return [
        {
            "id": mod.SCENARIO_META["id"],
            "name": mod.SCENARIO_META["name"],
            "icon": mod.SCENARIO_META["icon"],
            "description": mod.SCENARIO_META["description"],
            "welcome": mod.SCENARIO_META["welcome"],
            "examples": mod.SCENARIO_META["examples"],
        }
        for mod in SCENARIOS.values()
    ]
