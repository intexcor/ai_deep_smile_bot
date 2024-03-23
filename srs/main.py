from dotenv import load_dotenv
from os import getenv
import os
import asyncio

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart

from deepface import DeepFace

load_dotenv()
# Ваши токен бота и инициализация
TOKEN = getenv("BOT_TOKEN")


router = Router()


# Обработка команды /start
@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот, который может анализировать эмоции на фотографиях. Просто отправь мне фото, и я попробую "
        "угадать эмоцию!")


# Обработка фото
@router.message(F.photo)
async def handle_photo(message: types.Message, bot: Bot):
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
        emotions = await analyze_emotions(temp_image_path)

        # Выбор юникода смайлика на основе анализа эмоций
        chosen_emoji = await choose_emoji(emotions)

        # Удаление временного файла
        os.remove(temp_image_path)

        # Отправка смайлика
        await message.reply(chosen_emoji)
        # await message.reply(res)
        await message.reply(f"Эмоция :{await en_to_ru(max(emotions, key=emotions.get))}")
    except ValueError:
        await message.reply("На фотографии не обнаружено лиц. Пожалуйста, отправьте фото с лицом для анализа эмоций.")


async def analyze_emotions(image_file):
    result = DeepFace.analyze(img_path=image_file, actions=['emotion'], detector_backend='retinaface')
    return result[0]['emotion']


async def en_to_ru(text):
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


async def choose_emoji(emotions):
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


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, default=DefaultBotProperties())
    # And the run events dispatching
    dp = Dispatcher(maintenance_mode=True)
    # Maintenance-роутер должен быть первый
    dp.include_routers(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
