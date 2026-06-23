"""
物流场景配置：单号查询、航班状态、清关状态、延误分析
"""

import re
from datetime import datetime, timedelta

# 场景元信息
SCENARIO_META = {
    "id": "logistics",
    "name": "智慧物流",
    "icon": "🚚",
    "description": "国际物流追踪 · 航班监控 · 清关查询 · 延误分析",
    "welcome": "您好！我是智慧物流助手，可帮您查询运单、航班、清关及延误信息。",
    "examples": [
        "帮我查一下运单 SF1234567890 的物流状态",
        "CA1234 航班今天状态怎么样？",
        "运单 DHL9876543210 清关进度如何？",
        "分析一下 FedEx5555666677 为什么延误了",
    ],
}

# 实体提取正则（第一层防幻觉：信息完整性检查）
ENTITY_PATTERNS = {
    "tracking_number": re.compile(
        r"(?:运单|单号|快递|包裹|tracking)?\s*[:：]?\s*"
        r"([A-Z]{2,4}\d{8,12}|SF\d{10,12}|DHL\d{8,12}|FedEx\d{8,12})",
        re.IGNORECASE,
    ),
    "flight_number": re.compile(
        r"(?:航班|flight)?\s*[:：]?\s*([A-Z]{2}\d{3,4})",
        re.IGNORECASE,
    ),
}

# 意图识别关键词
INTENT_KEYWORDS = {
    "tracking_query": ["物流", "运单", "快递", "包裹", "追踪", "查询", "到哪", "状态"],
    "flight_status": ["航班", "飞机", "起飞", "降落", "flight"],
    "customs_status": ["清关", "海关", "报关", "入境", "customs"],
    "delay_analysis": ["延误", "延迟", "晚到", "为什么", "原因", "delay"],
}

# 各意图所需实体
INTENT_REQUIRED_ENTITIES = {
    "tracking_query": ["tracking_number"],
    "flight_status": ["flight_number"],
    "customs_status": ["tracking_number"],
    "delay_analysis": ["tracking_number"],
}

# 缺失实体时的追问模板
FOLLOWUP_TEMPLATES = {
    "tracking_number": "请提供您的运单号（例如 SF1234567890 或 DHL9876543210），以便我为您查询。",
    "flight_number": "请提供航班号（例如 CA1234 或 MU5678），以便我查询航班状态。",
}

# Mock 运单数据库
MOCK_TRACKING_DB = {
    "SF1234567890": {
        "carrier": "顺丰国际",
        "origin": "深圳",
        "destination": "洛杉矶",
        "status": "运输中",
        "current_location": "上海浦东转运中心",
        "estimated_delivery": "2026-06-25",
        "events": [
            {"time": "2026-06-20 14:30", "desc": "深圳揽收"},
            {"time": "2026-06-21 09:15", "desc": "出口报关完成"},
            {"time": "2026-06-22 18:40", "desc": "到达上海转运中心"},
        ],
    },
    "DHL9876543210": {
        "carrier": "DHL Express",
        "origin": "广州",
        "destination": "法兰克福",
        "status": "清关中",
        "current_location": "法兰克福机场海关",
        "estimated_delivery": "2026-06-24",
        "events": [
            {"time": "2026-06-19 10:00", "desc": "广州揽收"},
            {"time": "2026-06-21 22:30", "desc": "航班 CA931 起飞"},
            {"time": "2026-06-22 06:45", "desc": "到达法兰克福"},
        ],
    },
    "FedEx5555666677": {
        "carrier": "FedEx",
        "origin": "义乌",
        "destination": "纽约",
        "status": "延误",
        "current_location": "Anchorage 中转站",
        "estimated_delivery": "2026-06-28",
        "delay_reason": "阿拉斯加天气原因导致中转延误",
        "events": [
            {"time": "2026-06-18 08:00", "desc": "义乌揽收"},
            {"time": "2026-06-20 16:20", "desc": "航班 FX88 起飞"},
            {"time": "2026-06-21 03:00", "desc": "Anchorage 中转延误"},
        ],
    },
}

# Mock 航班数据库
MOCK_FLIGHT_DB = {
    "CA1234": {
        "airline": "中国国际航空",
        "route": "北京 PEK → 洛杉矶 LAX",
        "scheduled_departure": "2026-06-23 14:30",
        "scheduled_arrival": "2026-06-23 11:00",
        "actual_departure": "2026-06-23 15:10",
        "status": "飞行中",
        "altitude": "10668m",
        "speed": "890km/h",
    },
    "MU5678": {
        "airline": "中国东方航空",
        "route": "上海 PVG → 法兰克福 FRA",
        "scheduled_departure": "2026-06-23 01:30",
        "scheduled_arrival": "2026-06-23 07:45",
        "actual_departure": "2026-06-23 01:28",
        "status": "已到达",
        "gate": "B12",
    },
}

# Mock 清关数据库
MOCK_CUSTOMS_DB = {
    "SF1234567890": {
        "status": "待清关",
        "customs_office": "洛杉矶海关",
        "declaration_time": None,
        "estimated_clearance": "2026-06-24",
        "required_docs": ["商业发票", "装箱单"],
    },
    "DHL9876543210": {
        "status": "清关审核中",
        "customs_office": "法兰克福机场海关",
        "declaration_time": "2026-06-22 08:30",
        "estimated_clearance": "2026-06-23",
        "required_docs": ["商业发票", "原产地证", "检验检疫证明"],
        "inspector_note": "需补充商品编码说明",
    },
}

# RAG 知识库片段
RAG_KNOWLEDGE = {
    "tracking_query": [
        "国际快递通常包含揽收、出口报关、国际运输、进口清关、末端派送五个阶段。",
        "顺丰国际 SF 单号格式为 SF + 10-12 位数字。",
    ],
    "flight_status": [
        "货运航班状态包括：计划、延误、飞行中、已到达、取消。",
        "跨太平洋航线常见经停 Anchorage 中转。",
    ],
    "customs_status": [
        "进口清关一般需要商业发票、装箱单、原产地证等材料。",
        "清关状态：待申报 → 审核中 → 放行 / 查验。",
    ],
    "delay_analysis": [
        "常见延误原因：天气、航班调配、清关查验、末端派送积压。",
        "Anchorage 中转站冬季常因暴雪导致大面积延误。",
    ],
}


def extract_entities(text: str) -> dict:
    """从用户输入中提取物流相关实体"""
    entities = {}
    for name, pattern in ENTITY_PATTERNS.items():
        match = pattern.search(text)
        if match:
            entities[name] = match.group(1).upper()
    return entities


def detect_intent(text: str) -> str:
    """基于关键词匹配识别用户意图"""
    text_lower = text.lower()
    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[intent] = score
    if not scores:
        return "tracking_query"
    return max(scores, key=scores.get)


def get_intent_label(intent: str) -> str:
    """获取意图的中文标签"""
    labels = {
        "tracking_query": "运单查询",
        "flight_status": "航班状态",
        "customs_status": "清关状态",
        "delay_analysis": "延误分析",
    }
    return labels.get(intent, intent)


def get_tools() -> dict:
    """返回场景可用工具定义"""
    return {
        "query_tracking": {
            "name": "query_tracking",
            "label": "运单查询",
            "description": "根据运单号查询物流轨迹和当前状态",
            "params": ["tracking_number"],
        },
        "query_flight_status": {
            "name": "query_flight_status",
            "label": "航班状态",
            "description": "查询指定航班的实时状态",
            "params": ["flight_number"],
        },
        "query_customs_status": {
            "name": "query_customs_status",
            "label": "清关状态",
            "description": "查询运单的清关进度",
            "params": ["tracking_number"],
        },
        "analyze_delay": {
            "name": "analyze_delay",
            "label": "延误分析",
            "description": "分析运单延误原因并给出预计到达时间",
            "params": ["tracking_number"],
        },
    }


def get_tool_for_intent(intent: str) -> str:
    """根据意图映射对应工具"""
    mapping = {
        "tracking_query": "query_tracking",
        "flight_status": "query_flight_status",
        "customs_status": "query_customs_status",
        "delay_analysis": "analyze_delay",
    }
    return mapping.get(intent, "query_tracking")


def execute_tool(tool_name: str, params: dict) -> dict:
    """执行 Mock 工具并返回结果"""
    if tool_name == "query_tracking":
        return _query_tracking(params.get("tracking_number", ""))
    if tool_name == "query_flight_status":
        return _query_flight_status(params.get("flight_number", ""))
    if tool_name == "query_customs_status":
        return _query_customs_status(params.get("tracking_number", ""))
    if tool_name == "analyze_delay":
        return _analyze_delay(params.get("tracking_number", ""))
    return {"success": False, "error": "未知工具", "validation_error": True}


def _query_tracking(tracking_number: str) -> dict:
    """Mock 运单查询工具"""
    tracking_number = tracking_number.upper()
    if tracking_number not in MOCK_TRACKING_DB:
        return {
            "success": False,
            "error": f"未找到运单 {tracking_number}，请确认单号是否正确",
            "validation_error": True,
        }
    data = MOCK_TRACKING_DB[tracking_number]
    return {"success": True, "data": data, "tracking_number": tracking_number}


def _query_flight_status(flight_number: str) -> dict:
    """Mock 航班状态查询工具"""
    flight_number = flight_number.upper()
    if flight_number not in MOCK_FLIGHT_DB:
        return {
            "success": False,
            "error": f"未找到航班 {flight_number} 的信息",
            "validation_error": True,
        }
    data = MOCK_FLIGHT_DB[flight_number]
    return {"success": True, "data": data, "flight_number": flight_number}


def _query_customs_status(tracking_number: str) -> dict:
    """Mock 清关状态查询工具"""
    tracking_number = tracking_number.upper()
    if tracking_number not in MOCK_CUSTOMS_DB:
        return {
            "success": False,
            "error": f"运单 {tracking_number} 暂无清关记录",
            "validation_error": True,
        }
    data = MOCK_CUSTOMS_DB[tracking_number]
    return {"success": True, "data": data, "tracking_number": tracking_number}


def _analyze_delay(tracking_number: str) -> dict:
    """Mock 延误分析工具"""
    tracking_number = tracking_number.upper()
    if tracking_number not in MOCK_TRACKING_DB:
        return {
            "success": False,
            "error": f"未找到运单 {tracking_number}",
            "validation_error": True,
        }
    data = MOCK_TRACKING_DB[tracking_number]
    if data.get("status") != "延误":
        return {
            "success": True,
            "data": {
                "is_delayed": False,
                "status": data["status"],
                "message": f"运单当前状态为「{data['status']}」，未检测到延误。",
            },
            "tracking_number": tracking_number,
        }
    return {
        "success": True,
        "data": {
            "is_delayed": True,
            "delay_reason": data.get("delay_reason", "未知原因"),
            "current_location": data["current_location"],
            "original_eta": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "new_eta": data["estimated_delivery"],
            "delay_days": 3,
            "recommendation": "建议联系客服申请延误补偿",
        },
        "tracking_number": tracking_number,
    }


def format_final_answer(intent: str, tool_result: dict, entities: dict) -> str:
    """根据工具结果生成最终回复"""
    if not tool_result.get("success"):
        return tool_result.get("error", "查询失败，请稍后重试。")

    data = tool_result.get("data", {})

    if intent == "tracking_query":
        events_text = "\n".join(
            f"  · {e['time']} — {e['desc']}" for e in data.get("events", [])
        )
        return (
            f"📦 运单 **{tool_result['tracking_number']}** 查询结果：\n\n"
            f"承运商：{data['carrier']}\n"
            f"路线：{data['origin']} → {data['destination']}\n"
            f"当前状态：**{data['status']}**\n"
            f"当前位置：{data['current_location']}\n"
            f"预计送达：{data['estimated_delivery']}\n\n"
            f"物流轨迹：\n{events_text}"
        )

    if intent == "flight_status":
        return (
            f"✈️ 航班 **{tool_result['flight_number']}** 状态：\n\n"
            f"航司：{data['airline']}\n"
            f"航线：{data['route']}\n"
            f"计划起飞：{data['scheduled_departure']}\n"
            f"实际起飞：{data.get('actual_departure', '—')}\n"
            f"当前状态：**{data['status']}**"
            + (f"\n高度：{data['altitude']}" if "altitude" in data else "")
            + (f"\n速度：{data['speed']}" if "speed" in data else "")
        )

    if intent == "customs_status":
        docs = "、".join(data.get("required_docs", []))
        return (
            f"🛃 运单 **{tool_result['tracking_number']}** 清关状态：\n\n"
            f"清关状态：**{data['status']}**\n"
            f"海关：{data['customs_office']}\n"
            f"预计放行：{data.get('estimated_clearance', '—')}\n"
            f"所需材料：{docs}"
            + (
                f"\n备注：{data['inspector_note']}"
                if data.get("inspector_note")
                else ""
            )
        )

    if intent == "delay_analysis":
        if not data.get("is_delayed"):
            return data.get("message", "未检测到延误。")
        return (
            f"⏰ 运单 **{tool_result['tracking_number']}** 延误分析：\n\n"
            f"延误原因：{data['delay_reason']}\n"
            f"当前位置：{data['current_location']}\n"
            f"原预计到达：{data['original_eta']}\n"
            f"新预计到达：**{data['new_eta']}**（延误 {data['delay_days']} 天）\n"
            f"建议：{data['recommendation']}"
        )

    return "查询完成。"
