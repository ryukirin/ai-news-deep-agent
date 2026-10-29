import json

def ask_decision(action, allowed):
    name = action["name"]
    args = action.get("arguments", action.get("args", {}))
    print(f"\n工具: {name}\n参数: {json.dumps(args, ensure_ascii=False)}\n可选决策: {', '.join(allowed)}")
    while True:                                    # 输入不在允许范围内就重新输入
        choice = input("请输入决策: ").strip()
        if choice in allowed:
            break
        print(f"只能输入 {', '.join(allowed)} 之一")

    if choice == "approve":
        return {"type": "approve"}
    if choice == "edit":                           # 逐个参数询问，直接回车保留原值
        new_args = {}
        for key, value in args.items():
            text = input(f"  {key}（直接回车保留 {value!r}）: ").strip()
            new_args[key] = text if text else value
        return {"type": "edit", "edited_action": {"name": name, "args": new_args}}
    if choice == "reject":                         # 原因可留空，留空时用中间件的默认反馈
        decision = {"type": "reject"}
        reason = input("拒绝原因（可留空）: ").strip()
        if reason:
            decision["message"] = reason
        return decision
    return {"type": "respond", "message": input("回答: ").strip()}