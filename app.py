"""
Flask 主服务：提供 Web 页面与 SSE 流式接口
"""

import json
from flask import Flask, Response, render_template, request, jsonify

from agent_engine import ReActEngine, get_scenario_list

app = Flask(__name__)

# 会话级实体缓存（简单内存存储，演示用）
session_store: dict[str, dict] = {}


@app.route("/")
def index():
    """渲染主页面"""
    return render_template("index.html")


@app.route("/api/scenarios")
def api_scenarios():
    """返回可用场景列表"""
    return jsonify(get_scenario_list())


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    SSE 流式聊天接口
    请求体：{"message": "...", "scenario": "logistics", "session_id": "xxx"}
    """
    body = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()
    scenario_id = body.get("scenario", "logistics")
    session_id = body.get("session_id", "default")

    if not message:
        return jsonify({"error": "消息不能为空"}), 400

    # 恢复会话实体（支持多轮追问）
    session_entities = session_store.get(session_id, {})
    engine = ReActEngine(scenario_id, session_entities)

    def generate():
        """SSE 生成器"""
        for event in engine.run(message):
            yield event
            # 解析 complete 事件以保存会话实体
            if '"type": "complete"' in event or '"type":"complete"' in event:
                try:
                    raw = event.replace("data: ", "").strip()
                    data = json.loads(raw)
                    session_store[session_id] = data.get("session_entities", {})
                except (json.JSONDecodeError, KeyError):
                    pass

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """重置会话实体缓存"""
    body = request.get_json(silent=True) or {}
    session_id = body.get("session_id", "default")
    session_store.pop(session_id, None)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
