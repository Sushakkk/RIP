from minio import Minio
from django.contrib.auth.models import User
from app.models import Activities
from django.core.management.base import BaseCommand







def add_users():
    # Создание пользователей из твоих данных
    User.objects.create_superuser("admin", "root@root.com", "1")
    User.objects.create_user(username="sushakkk", first_name="Ксения", last_name="Карпова", password="789451ksenia")
    User.objects.create_user(username="moderator1", first_name="Мария", last_name="Гостюнина", password="789451ksenia")
    User.objects.create_user(username="moderator2", first_name="Вензель", last_name="Малиновый", password="789451ksenia")
    # User.objects.create_user(username="user1", first_name="user1", last_name="user1", password="789451ksenia")
    # User.objects.create_user(username="user2", first_name="user2", last_name="user2", password="789451ksenia")

    print("Пользователи добавлены")

def add_activities():
    activities = [
        {
            "title": "Маникюр и педикюр",
            "description": "Оказание профессиональных услуг маникюра и педикюра...",
            "img_url": "http://127.0.0.1:9000/flexwork/1.png",
            "category": "Красота и здоровье",
            "status": "active"
        },
        {
            "title": "Услуги косметолога",
            "description": "Комплексные услуги по уходу за кожей лица и тела...",
            "img_url": "http://127.0.0.1:9000/flexwork/2.jpg",
            "category": "Красота и здоровье",
            "status": "active"
        },
        {

        'title': 'Ремонт бытовой техники',
        'img_url': 'http://127.0.0.1:9000/flexwork/3.jpg',
        'description': 'Оказание услуг по ремонту бытовой техники на дому с быстрым и качественным решением проблем с техникой.',
        'category': 'Бытовые услуги',
  
    },
    {

        'title': 'Консультации по медицинским вопросам',
        'img_url': 'http://127.0.0.1:9000/flexwork/4.webp',
       
        'description': 'Консультации и рекомендации по медицинским вопросам от опытных врачей и специалистов.',
       
        'category': 'Красота и здоровье',
    },
    {

        'title': 'Репетитор по Английскому языку',
        'img_url': 'http://127.0.0.1:9000/flexwork/5.png',
       
        'description': 'Проведение индивидуальных и групповых занятий по английскому языку для детей, подростков и взрослых. ',
       
        'category': 'Образование',


    },
    {
 
        'title': 'Уборка и клининг',
        'img_url': 'http://127.0.0.1:9000/flexwork/6.webp',
       
        'description': 'Предоставление профессиональных услуг по уборке и клинингу жилых и коммерческих помещений с использованием качественных чистящих средств и современного оборудования. Услуги включают как разовые генеральные уборки, так и регулярное поддержание чистоты.',
        'category': 'Бытовые услуги',
    },
    ]

    for activity in activities:
        Activities.objects.create(**activity)

    print("Деятельности добавлены")

def upload_images_to_minio():
    client = Minio("minio:9000", "minio", "minio123", secure=False)
    images = ["1.png", "2.jpg", "3.jpg", "4.webp", "5.png", "6.webp"]
    
    for image in images:
        client.fput_object("flexwork", image, f"app/static/images/{image}")

    print("Изображения загружены")

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_activities()


