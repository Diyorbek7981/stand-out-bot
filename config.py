from dotenv import dotenv_values
from aiogram import Bot

ENV = dotenv_values(".env")

Token = ENV["TOKEN"]
ADMIN = ENV["ADMIN"]
API = ENV["API"]
CHANNEL = ENV["CHANNEL"]

bot = Bot(token=Token)