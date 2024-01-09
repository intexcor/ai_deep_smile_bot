import os
from aiogram.types import Message
# import cv2
# import numpy as np
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
# from aiogram.types import ParseMode
# from aiogram.utils import executor
# from PIL import Image
from deepface import DeepFace

# Ваши токен бота и инициализация
BOT_TOKEN = 'your_token'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# Обработка команды /start
@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.reply(
        "Привет! Я бот, который может анализировать эмоции на фотографиях. Просто отправь мне фото, и я попробую "
        "угадать эмоцию!")


# Обработка фото
@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def handle_photo(message: types.Message):
    try:
        # Получаем информацию о фото
        photo = message.photo[-1]
        photo_id = photo.file_id

        # Загрузка фото
        photo_obj = await bot.get_file(photo_id)
        photo_path = photo_obj.file_path
        photo_file = await bot.download_file(photo_path)

        # Создание временного файла для изображения
        temp_image_path = f'temp_image_{photo_id}.jpg'
        with open(temp_image_path, 'wb') as temp_image:
            temp_image.write(photo_file.read())

        # Анализ эмоций на фото
        emotions = analyze_emotions(temp_image_path)

        # Выбор юникода смайлика на основе анализа эмоций
        chosen_emoji = choose_emoji(emotions)

        # Удаление временного файла
        os.remove(temp_image_path)

        # Отправка смайлика
        await message.reply(chosen_emoji)
        # await message.reply(res)
        await message.reply(f"Эмоция :{en_to_ru(max(emotions, key=emotions.get))}")
    except ValueError:
        await message.reply("На фотографии не обнаружено лиц. Пожалуйста, отправьте фото с лицом для анализа эмоций.")


def analyze_emotions(image_file):

    result = DeepFace.analyze(img_path=image_file, actions=['emotion'], detector_backend='retinaface')
    return result[0]['emotion']


def en_to_ru(text):
    emotion_mapping = {
        'angry': 'гнев',
        'disgust': 'отвращение',
        'fear': 'страх',
        'happy': 'радость',
        'sad': 'грусть',
        'surprise': 'удивление',
        'neutral': 'нейтральность'
    }
    perev = emotion_mapping[text]
    return perev


def choose_emoji(emotions):
    # Эмоции и соответствующие юникоды смайликов
    emoji_mapping = {
        'angry': '😡',
        'disgust': '🤢',
        'fear': '😨',
        'happy': '😄',
        'sad': '😢',
        'surprise': '😲',
        'neutral': '😐'
    }

    # Находим эмоцию с наивысшей вероятностью
    max_emotion = max(emotions, key=emotions.get)

    # Возвращаем юникод смайлика, соответствующего наиболее вероятной эмоции
    return emoji_mapping.get(max_emotion, '😐')  # Если эмоция не найдена, используем нейтральный смайлик


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
