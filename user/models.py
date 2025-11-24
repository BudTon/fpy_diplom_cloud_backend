import uuid
from django.db import models
from django.contrib.auth.models import User


# Функция для динамического формирования пути для загрузки файлов
def user_directory_path(instance, filename):
    """
    Формирует путь для сохранения файлов:
    storage/user_<username>_<id>/<filename>
    """
    return f"user_{instance.user.username}_{instance.user.id}/{filename}"


class File(models.Model):
    # Первичный ключ (автоинкрементный int)
    id = models.AutoField(primary_key=True)

    # Связь с пользователем
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Название файла
    file_name = models.CharField(max_length=200, unique=False, default="Unnamed")

    # Загружаемый файл
    file = models.FileField(
        upload_to=user_directory_path, default="path/to/default/file"
    )

    # Скрытая ссылка
    short_hash = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Дата загрузки файла
    created_at = models.DateTimeField(auto_now_add=True)

    # Дата последнего скачивания файла (может быть пустой)
    lastDownloadDate = models.DateTimeField(null=True, blank=True)

    # Размер файла в байтах (необходимо положительное целое число)
    size = models.PositiveIntegerField(default=0)

    # Комментарий к файлу (может отсутствовать)
    comment = models.CharField(max_length=250, null=True, blank=True)

    # # Ссылка на файл или внешний ресурс (может отсутствовать)
    # link = models.URLField(max_length=200, null=True, blank=True)

    # Новое поле для хранения ссылок в виде словаря
    links = models.JSONField(default=dict, blank=True, null=True)

    # Тип файла
    type = models.CharField(max_length=50, default="unknown")

    def __str__(self):
        return f"{self.file.name} ({self.user.username})"
