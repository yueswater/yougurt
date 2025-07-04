def check_if_user_exists(user_id: str) -> bool:     # Mock version
    existing_user_ids = {"U5bd3d61b7c6235a344238adbe25df5df1", "U654321"}
    return user_id in existing_user_ids
