# 暂时全部以 local-user 作为用户身份
def user_namespace(rt):
    if rt.server_info and rt.server_info.user:
        return (rt.server_info.user.identity,)
    user_id = getattr(rt.context, "user_id", "local-user")
    return (user_id,)