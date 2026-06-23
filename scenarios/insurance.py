"""
保险场景配置：保单查询、理赔咨询、材料清单（多轮追问演示）
"""

import re

# 场景元信息
SCENARIO_META = {
    "id": "insurance",
    "name": "智能保险",
    "icon": "🛡️",
    "description": "保单查询 · 理赔咨询 · 材料清单 · 多轮智能追问",
    "welcome": "您好！我是智能保险助手，可帮您查询保单、咨询理赔及获取材料清单。",
    "examples": [
        "帮我查一下保单 P2024001234 的信息，身份证 110101199001011234",
        "我想咨询一下医疗险理赔流程",
        "重疾险理赔需要准备哪些材料？",
    ],
}

# 实体提取正则
ENTITY_PATTERNS = {
    "policy_number": re.compile(
        r"(?:保单|policy)?\s*[:：]?\s*(P\d{10,12}|INS\d{8,12})",
        re.IGNORECASE,
    ),
    "id_number": re.compile(
        r"(?:身份证|证件号)?\s*[:：]?\s*(\d{17}[\dXx])",
        re.IGNORECASE,
    ),
    "claim_type": re.compile(
        r"(医疗险|重疾险|意外险|寿险|车险|财产险|医疗|重疾|意外)",
        re.IGNORECASE,
    ),
}

# 意图识别关键词
INTENT_KEYWORDS = {
    "policy_query": ["保单", "保险", "查询", "保障", "保费", "保额"],
    "claim_consultation": ["理赔", "报销", "赔付", "申请", "流程", "怎么赔"],
    "material_list": ["材料", "清单", "准备", "文件", "资料", "需要什么"],
}

# 各意图所需实体（material_list 仅需 claim_type，演示多轮追问）
INTENT_REQUIRED_ENTITIES = {
    "policy_query": ["policy_number", "id_number"],
    "claim_consultation": ["claim_type"],
    "material_list": ["claim_type"],
}

# 缺失实体追问模板
FOLLOWUP_TEMPLATES = {
    "policy_number": "请提供您的保单号（例如 P2024001234），以便我为您查询。",
    "id_number": "为保障信息安全，请提供投保人身份证号码后四位或完整号码。",
    "claim_type": "请问您咨询的是哪种保险类型？（医疗险 / 重疾险 / 意外险 / 寿险 / 车险）",
}

# Mock 保单数据库
MOCK_POLICY_DB = {
    "P2024001234": {
        "holder": "张三",
        "id_number": "110101199001011234",
        "product": "康乐一生重疾险",
        "type": "重疾险",
        "premium": "6800元/年",
        "coverage": "50万元",
        "start_date": "2024-01-15",
        "end_date": "2044-01-14",
        "status": "有效",
        "beneficiaries": ["李四（配偶）"],
    },
    "P2024005678": {
        "holder": "王五",
        "id_number": "310101198505051234",
        "product": "安心医疗险",
        "type": "医疗险",
        "premium": "1200元/年",
        "coverage": "200万元",
        "start_date": "2024-03-01",
        "end_date": "2025-02-28",
        "status": "有效",
        "beneficiaries": ["王五（本人）"],
    },
}

# Mock 理赔流程知识
CLAIM_PROCESS = {
    "医疗险": {
        "steps": [
            "1. 出险后 48 小时内拨打客服热线 955XX 报案",
            "2. 收集住院发票、费用清单、诊断证明",
            "3. 通过 APP 或线下提交理赔申请",
            "4. 审核周期 3-5 个工作日",
            "5. 赔款打入指定银行账户",
        ],
        "hotline": "955XX",
        "note": "急诊可先治疗后补材料，但需在 30 日内提交",
    },
    "重疾险": {
        "steps": [
            "1. 确诊后第一时间联系专属顾问",
            "2. 提交病理报告、诊断证明、住院病历",
            "3. 填写理赔申请书并签署授权书",
            "4. 公司派调查员核实（如需）",
            "5. 审核通过后 10 日内一次性赔付",
        ],
        "hotline": "955XX",
        "note": "需在确诊后 2 年内申请，逾期可能丧失索赔权",
    },
    "意外险": {
        "steps": [
            "1. 发生意外后立即报案（24 小时内）",
            "2. 提供事故证明（交警/公安出具）",
            "3. 提交医疗发票和伤残鉴定（如适用）",
            "4. 审核 5-7 个工作日",
            "5. 赔款到账",
        ],
        "hotline": "955XX",
        "note": "高风险运动导致的意外可能不在保障范围内",
    },
}

# Mock 材料清单
MATERIAL_LISTS = {
    "医疗险": [
        "理赔申请书（公司官网下载）",
        "被保险人身份证复印件",
        "银行卡复印件",
        "门诊/住院发票原件",
        "费用明细清单",
        "诊断证明书 / 出院小结",
        "检查报告（CT/MRI 等）",
    ],
    "重疾险": [
        "理赔申请书",
        "被保险人身份证",
        "银行卡信息",
        "病理诊断报告（原件）",
        "出院记录 / 住院病历",
        "相关检查报告",
        "授权委托书（如代办）",
    ],
    "意外险": [
        "理赔申请书",
        "身份证 / 户口本",
        "意外事故证明",
        "医疗发票及清单",
        "伤残鉴定报告（伤残理赔）",
        "死亡证明（身故理赔）",
    ],
    "寿险": [
        "理赔申请书",
        "死亡证明",
        "户口注销证明",
        "受益人身份证",
        "银行卡信息",
        "保险合同原件",
    ],
    "车险": [
        "行驶证、驾驶证",
        "交通事故责任认定书",
        "维修发票",
        "现场照片",
        "银行卡信息",
    ],
}

# 险种名称标准化映射
CLAIM_TYPE_NORMALIZE = {
    "医疗": "医疗险",
    "医疗险": "医疗险",
    "重疾": "重疾险",
    "重疾险": "重疾险",
    "意外": "意外险",
    "意外险": "意外险",
    "寿险": "寿险",
    "车险": "车险",
    "财产险": "财产险",
}

# RAG 知识库
RAG_KNOWLEDGE = {
    "policy_query": [
        "保单查询需验证投保人身份，需提供保单号和身份证号码。",
        "有效保单状态包括：有效、暂停、终止、满期。",
    ],
    "claim_consultation": [
        "理赔黄金法则：及时报案、保留证据、如实告知。",
        "不同险种理赔时效和材料要求差异较大。",
    ],
    "material_list": [
        "材料清单因险种和具体案件而异，建议以官方最新要求为准。",
        "所有复印件建议标注「仅供理赔使用」。",
    ],
}


def extract_entities(text: str) -> dict:
    """从用户输入中提取保险相关实体"""
    entities = {}
    for name, pattern in ENTITY_PATTERNS.items():
        match = pattern.search(text)
        if match:
            value = match.group(1)
            if name == "claim_type":
                entities[name] = CLAIM_TYPE_NORMALIZE.get(value, value)
            elif name == "policy_number":
                entities[name] = value.upper()
            else:
                entities[name] = value.upper() if name == "id_number" else value
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
        return "claim_consultation"
    return max(scores, key=scores.get)


def get_intent_label(intent: str) -> str:
    """获取意图的中文标签"""
    labels = {
        "policy_query": "保单查询",
        "claim_consultation": "理赔咨询",
        "material_list": "材料清单",
    }
    return labels.get(intent, intent)


def get_tools() -> dict:
    """返回场景可用工具定义"""
    return {
        "query_policy": {
            "name": "query_policy",
            "label": "保单查询",
            "description": "根据保单号和身份证验证并查询保单详情",
            "params": ["policy_number", "id_number"],
        },
        "claim_consultation": {
            "name": "claim_consultation",
            "label": "理赔咨询",
            "description": "提供指定险种的理赔流程指导",
            "params": ["claim_type"],
        },
        "get_material_list": {
            "name": "get_material_list",
            "label": "材料清单",
            "description": "获取指定险种理赔所需材料清单",
            "params": ["claim_type"],
        },
    }


def get_tool_for_intent(intent: str) -> str:
    """根据意图映射对应工具"""
    mapping = {
        "policy_query": "query_policy",
        "claim_consultation": "claim_consultation",
        "material_list": "get_material_list",
    }
    return mapping.get(intent, "claim_consultation")


def execute_tool(tool_name: str, params: dict) -> dict:
    """执行 Mock 工具并返回结果"""
    if tool_name == "query_policy":
        return _query_policy(
            params.get("policy_number", ""),
            params.get("id_number", ""),
        )
    if tool_name == "claim_consultation":
        return _claim_consultation(params.get("claim_type", ""))
    if tool_name == "get_material_list":
        return _get_material_list(params.get("claim_type", ""))
    return {"success": False, "error": "未知工具", "validation_error": True}


def _query_policy(policy_number: str, id_number: str) -> dict:
    """Mock 保单查询工具（含身份校验）"""
    policy_number = policy_number.upper()
    id_number = id_number.upper()

    if policy_number not in MOCK_POLICY_DB:
        return {
            "success": False,
            "error": f"未找到保单 {policy_number}，请确认保单号是否正确",
            "validation_error": True,
        }

    policy = MOCK_POLICY_DB[policy_number]
    if policy["id_number"].upper() != id_number:
        return {
            "success": False,
            "error": "身份证号码与保单信息不匹配，无法查询",
            "validation_error": True,
        }

    return {"success": True, "data": policy, "policy_number": policy_number}


def _claim_consultation(claim_type: str) -> dict:
    """Mock 理赔咨询工具"""
    claim_type = CLAIM_TYPE_NORMALIZE.get(claim_type, claim_type)
    if claim_type not in CLAIM_PROCESS:
        return {
            "success": False,
            "error": f"暂不支持 {claim_type} 的理赔咨询，请选择：医疗险/重疾险/意外险",
            "validation_error": True,
        }
    return {"success": True, "data": CLAIM_PROCESS[claim_type], "claim_type": claim_type}


def _get_material_list(claim_type: str) -> dict:
    """Mock 材料清单工具"""
    claim_type = CLAIM_TYPE_NORMALIZE.get(claim_type, claim_type)
    if claim_type not in MATERIAL_LISTS:
        return {
            "success": False,
            "error": f"暂无 {claim_type} 的材料清单，请选择：医疗险/重疾险/意外险/寿险/车险",
            "validation_error": True,
        }
    return {
        "success": True,
        "data": {"materials": MATERIAL_LISTS[claim_type]},
        "claim_type": claim_type,
    }


def format_final_answer(intent: str, tool_result: dict, entities: dict) -> str:
    """根据工具结果生成最终回复"""
    if not tool_result.get("success"):
        return tool_result.get("error", "查询失败，请稍后重试。")

    data = tool_result.get("data", {})

    if intent == "policy_query":
        beneficiaries = "、".join(data.get("beneficiaries", []))
        return (
            f"📋 保单 **{tool_result['policy_number']}** 查询结果：\n\n"
            f"投保人：{data['holder']}\n"
            f"产品名称：{data['product']}（{data['type']}）\n"
            f"保费：{data['premium']}\n"
            f"保额：{data['coverage']}\n"
            f"保障期间：{data['start_date']} 至 {data['end_date']}\n"
            f"状态：**{data['status']}**\n"
            f"受益人：{beneficiaries}"
        )

    if intent == "claim_consultation":
        steps_text = "\n".join(data["steps"])
        return (
            f"📞 **{tool_result['claim_type']}** 理赔流程：\n\n"
            f"{steps_text}\n\n"
            f"客服热线：{data['hotline']}\n"
            f"⚠️ 注意：{data['note']}"
        )

    if intent == "material_list":
        materials = data.get("materials", [])
        items_text = "\n".join(f"  {i + 1}. {m}" for i, m in enumerate(materials))
        return (
            f"📄 **{tool_result['claim_type']}** 理赔材料清单：\n\n"
            f"{items_text}\n\n"
            f"💡 提示：所有复印件请标注「仅供理赔使用」，原件请妥善保管。"
        )

    return "查询完成。"
