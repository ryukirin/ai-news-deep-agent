import json

def ask_decision(action, allowed):
    name = action["name"]
    args = action.get("arguments", action.get("args", {}))
    print(f"\nTool: {name}\nArgs: {json.dumps(args, ensure_ascii=False)}\nAllowed decisions: {', '.join(allowed)}")
    while True:                                    # Ask again until the input is an allowed decision
        choice = input("Enter a decision: ").strip()
        if choice in allowed:
            break
        print(f"Enter one of: {', '.join(allowed)}")

    if choice == "approve":
        return {"type": "approve"}
    if choice == "edit":                           # Ask for each argument. Press Enter to keep the original value.
        new_args = {}
        for key, value in args.items():
            text = input(f"  {key} (press Enter to keep {value!r}): ").strip()
            new_args[key] = text if text else value
        return {"type": "edit", "edited_action": {"name": name, "args": new_args}}
    if choice == "reject":                         # The reason may be empty. The middleware's default feedback is used then.
        decision = {"type": "reject"}
        reason = input("Reason for rejection (optional): ").strip()
        if reason:
            decision["message"] = reason
        return decision
    return {"type": "respond", "message": input("Response: ").strip()}
