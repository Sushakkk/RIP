from lab3 import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *



from rest_framework.response import Response

client = Minio(
        endpoint="minio:9000",  # Используем имя контейнера MinIO, а не 'localhost'
        access_key="minio",
        secret_key="minio123",
        secure=False  # SSL не используется
    )


def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        # Загружаем файл в бакет 'flexwork'
        client.put_object('flexwork', image_name, file_object, file_object.size)
        return f"http://127.0.0.1:9000/flexwork/{image_name}"
    except Exception as e:
        return {"error": str(e)}

def add_pic_to_activity(activity, pic):
    # Создаем клиент MinIO с использованием ваших параметров
    

    # Генерация уникального имени для изображения на основе ID активности
    img_obj_name = f"{activity.id}.png"

    if not pic:
        return Response({"error": "Нет файла для изображения."})

    # Загружаем изображение через MinIO
    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)

    # Сохраняем URL изображения в поле img_url
    activity.img_url = result
    activity.save()

    return Response({"message": "Изображение успешно загружено", "img_url": result})




def remove_pic_from_activity(activity):
    img_obj_name = f"{activity.id}.png"  # Генерация имени файла для удаления

    try:
        # Удаляем объект из бакета 'flexwork'
        client.remove_object('flexwork', img_obj_name)
        return {"message": "Изображение успешно удалено"}
    except Exception as e:
        return {"error": str(e)}