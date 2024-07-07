def update_user_info(user, cleaned_data):
    """Метод для обновления данных пользователя."""
    user_data = cleaned_data["user"]
    if not user.first_name:
        user.first_name = user_data["first_name"]
    if not user.last_name:
        user.last_name = user_data["last_name"]
    if not user.phone:
        user.phone = user_data["phone"]
    user.save()
