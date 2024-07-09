import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.mongo import MongoStorage
from decouple import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor.motor_asyncio import AsyncIOMotorClient

# получаем список администраторов из .env
admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]

# настраиваем логирование и выводим в переменную для отдельного использования в нужных местах
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# инициируем объект, который будет отвечать за взаимодействие с базой данных
# db_manager = DatabaseManager(db_url=config('PG_LINK'), deletion_password=config('ROOT_PASS'))

scheduler = AsyncIOScheduler(timezone='Europe/Minsk')

# инициируем объект бота, передавая ему parse_mode=ParseMode.HTML по умолчанию
bot = Bot(token=config('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

client = AsyncIOMotorClient(config('MONGO_URL'))
db = client[config('MONGO_NAME')]

# инициируем объект бота
# dp = Dispatcher(storage=MemoryStorage())
dp = Dispatcher(storage=MongoStorage(client))
