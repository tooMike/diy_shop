import random
import string


from users.constants import CONFIRMATION_CODE_MAX_LENGTH


def create_confirmation_code(
    size=CONFIRMATION_CODE_MAX_LENGTH,
    chars=string.ascii_uppercase + string.digits
):
    """Генерируем код подтверждения."""
    return "".join(random.choice(chars) for _ in range(size))
