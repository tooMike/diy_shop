from rest_framework_simplejwt.tokens import AccessToken


def get_tokens_for_user(user):
    """Получаем токен для пользователя."""
    access = AccessToken.for_user(user)

    return {"token": str(access)}
