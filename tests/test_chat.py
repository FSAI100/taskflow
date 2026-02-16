"""
AI 评测：不追求 100% 通过（因为 LLM 有随机性），
但追求"大多数情况下做对"。需要配置真实的 API Key。
"""

import os
import pytest

EVAL_CASES = [
    {
        "input": "帮我创建一个任务：写周报",
        "expect_contains": ["创建", "周报"],
        "description": "应该创建任务",
    },
    {
        "input": "我有哪些待办任务？",
        "expect_contains": ["任务"],
        "description": "应该查询任务列表",
    },
    {
        "input": "总结一下我的任务情况",
        "expect_contains": ["总计"],
        "description": "应该返回统计",
    },
]


@pytest.mark.skipif(
    not os.getenv("DASHSCOPE_API_KEY"),
    reason="No DASHSCOPE_API_KEY set; skip AI eval",
)
@pytest.mark.parametrize("case", EVAL_CASES, ids=[c["description"] for c in EVAL_CASES])
def test_ai_response(client, case):
    # 先注册登录
    client.post(
        "/users/register",
        json={"username": "eval", "email": "e@e.com", "password": "123"},
    )
    login = client.post(
        "/users/login",
        json={"username": "eval", "password": "123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/chat/",
        json={"message": case["input"]},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    reply = res.json()["reply"]

    for keyword in case["expect_contains"]:
        assert keyword in reply, f"期望回复包含'{keyword}'，实际回复：{reply}"
