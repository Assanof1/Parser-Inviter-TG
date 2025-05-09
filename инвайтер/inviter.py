from telethon import TelegramClient, events, sync, functions
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import FloodWaitError
import asyncio
from datetime import datetime, timedelta
from telethon.tl.functions.channels import InviteToChannelRequest
import time
import os 
import datetime
import json 
from telethon.errors import UserPrivacyRestrictedError
import aiohttp
import threading
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError








API_ID = 24990728  # Замените на ваш API ID
API_HASH = '0d4be15713aa175def48fb3481eafe02'  # Замените на ваш API Hash
ACCOUNTS_DIR = 'acc'



# Константы для работы с аккаунтами и файлами
ACCOUNTS_DIR = "acc"
PROCESSED_USERS_FILE = "pars.txt"

def load_accounts():
    """
    Загружает список аккаунтов из папки acc.
    Возвращает список путей к файлам .session.
    """
    accounts = []
    if not os.path.exists(ACCOUNTS_DIR):
        os.makedirs(ACCOUNTS_DIR)  # Создаем папку, если её нет
    for filename in os.listdir(ACCOUNTS_DIR):
        if filename.endswith('.session'):
            accounts.append(os.path.join(ACCOUNTS_DIR, filename))
    return accounts


async def add_account(api_id, api_hash):
    """
    Добавляет новый аккаунт через ввод номера телефона.
    """
    phone = input("Введите номер телефона: ")
    session_file = os.path.join(ACCOUNTS_DIR, phone + '.session')
    client = TelegramClient(session_file, api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = input('Введите код: ')
            await client.sign_in(phone, code=code)
            print(f"Аккаунт {phone} успешно добавлен.")
    except Exception as e:
        print(f"Ошибка при добавлении аккаунта: {e}")
    finally:
        await client.disconnect()


def list_accounts():
    """
    Выводит список аккаунтов и предлагает удалить один из них.
    """
    accounts = load_accounts()
    if not accounts:
        print("Нет добавленных аккаунтов.")
        return
    print("Список аккаунтов:")
    for i, acc in enumerate(accounts):
        phone_number = os.path.basename(acc).replace('.session', '')
        print(f"{i + 1}. {phone_number}")
    delete = input("Введите номер аккаунта для удаления (или нажмите Enter для отмены): ")
    if delete:
        try:
            index_to_delete = int(delete) - 1
            account_to_delete = accounts[index_to_delete]
            os.remove(account_to_delete)
            print(f"Аккаунт {os.path.basename(account_to_delete)} удален.")
        except (ValueError, IndexError):
            print("Некорректный ввод.")

# Добавим обработку перехода на следующий username и управление аккаунтами при блокировке

async def invite_users(accounts, users_file, num_accounts_to_use, num_invites, chat_url, delay):
    """
    Приглашает пользователей в чат с учетом обработки ошибок и переключения между аккаунтами.
    """
    # Проверка существования файла с пользователями
    if not os.path.exists(users_file):
        print(f"Файл {users_file} не найден.")
        return

    # Загрузка списка пользователей из файла
    with open(users_file, 'r', encoding='utf-8') as f:
        usernames = [line.strip() for line in f if line.strip()]

    # Загрузка уже обработанных пользователей
    if os.path.exists(PROCESSED_USERS_FILE):
        with open(PROCESSED_USERS_FILE, 'r', encoding='utf-8') as f:
            processed_usernames = set(line.strip() for line in f if line.strip())
    else:
        processed_usernames = set()

    accounts_to_use = accounts[:num_accounts_to_use]
    invite_count = 0
    current_account_index = 0

    while invite_count < num_invites and usernames:
        account_session = accounts_to_use[current_account_index]
        client = TelegramClient(account_session)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"Аккаунт {account_session} не авторизован. Пожалуйста, авторизуйте аккаунт.")
                continue

           import asyncio
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import InviteToChannelRequest

# Функция для сохранения обработанных пользователей (исправленная)
def save_processed_users(processed_usernames):
    try:
        with open("processed_users.txt", "w") as file:  # Открываем файл на запись
            for username in processed_usernames:
                file.write(f"{username}\n")  # Записываем каждый username в новую строку
        print("Список обработанных пользователей успешно сохранен.")
    except Exception as e:
        print(f"Ошибка при сохранении обработанных пользователей: {e}")

# Основной код
async def main():
    # Пример данных
    chat_url = "your_chat_url_or_invite_link"
    usernames = ["user1", "user2", "user3"]  # Список пользователей для приглашения
    num_invites = 10  # Максимальное количество приглашений
    delay = 60  # Задержка между приглашениями в секундах
    accounts_to_use = ["account1.session", "account2.session"]  # Сессии аккаунтов
    current_account_index = 0
    processed_usernames = set()

    while True:
        account_session = accounts_to_use[current_account_index]
        client = TelegramClient(account_session, api_id="your_api_id", api_hash="your_api_hash")

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"Аккаунт {account_session} не авторизован.")
                continue

            # Получение ID чата
            try:
                if chat_url.startswith('+'):
                    chat = await client(ImportChatInviteRequest(chat_url[1:]))
                    chat_id = chat.chats[0].id
                else:
                    chat = await client.get_entity(chat_url)
                    chat_id = chat.id
            except Exception as e:
                print(f"Ошибка при подключении к чату: {e}")
                await client.disconnect()
                continue

            invite_count = 0

            # Цикл по пользователям
            while usernames and invite_count < num_invites:
                username = usernames.pop(0)  # Берем первого пользователя из списка
                if username in processed_usernames:
                    print(f"Пользователь {username} уже обработан. Пропускаем...")
                    continue

                try:
                    # Попытка пригласить пользователя
                    await client(InviteToChannelRequest(channel=chat_id, users=[username]))
                    print(f"Успешно приглашен {username} через аккаунт {account_session}")
                    invite_count += 1
                    processed_usernames.add(username)  # Добавляем в обработанные
                    save_processed_users(processed_usernames)  # Сохраняем в файл

                except FloodWaitError as e:
                    flood_time = e.seconds
                    print(f"Обнаружен FloodWaitError. Ожидание {flood_time} секунд...")
                    await asyncio.sleep(flood_time)
                    usernames.insert(0, username)  # Возвращаем пользователя в начало списка
                    break  # Переходим на следующий аккаунт

                except UserPrivacyRestrictedError:
                    print(f"Пользователь {username} ограничил приглашения.")
                    processed_usernames.add(username)  # Добавляем в обработанные
                    save_processed_users(processed_usernames)  # Сохраняем в файл

                except Exception as e:
                    error_message = str(e)
                    if "User is already in the chat" in error_message:
                        print(f"Пользователь {username} уже в чате.")
                        processed_usernames.add(username)  # Добавляем в обработанные
                        save_processed_users(processed_usernames)  # Сохраняем в файл
                    elif "Too many requests" in error_message or "was used too many times" in error_message:
                        print(f"Спам блок для аккаунта {account_session}. Переходим на следующий аккаунт.")
                        usernames.insert(0, username)  # Возвращаем пользователя в список
                        break  # Переходим на следующий аккаунт
                    else:
                        print(f"Ошибка при приглашении {username} через аккаунт {account_session}: {error_message}")
                        usernames.insert(0, username)  # Возвращаем пользователя в начало списка
                        break  # Переходим на следующий аккаунт

                await asyncio.sleep(delay)  # Задержка между инвайтами

        except Exception as e:
            print(f"Ошибка при работе с аккаунтом {account_session}: {e}")

        finally:
            await client.disconnect()
            # Переключаемся на следующий аккаунт
            current_account_index = (current_account_index + 1) % len(accounts_to_use)

# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())

    """
    Парсит чат Telegram по URL, используя несколько аккаунтов.
    Сохраняет имена пользователей в файл pars.txt.
    """
    if not os.path.exists("pars"):
        os.makedirs("pars")
    output_file = "pars/pars.txt"

    # Открываем файл для записи результатов
    with open(output_file, "w", encoding="utf-8") as f:
        # Перебираем аккаунты
        accounts = load_accounts()
        accounts_to_use = accounts[:account_session]
        for i, account_session in enumerate(accounts_to_use):
            session_file = account_session
            client = TelegramClient(session_file)
            try:
                await client.connect()
                if not await client.is_user_authorized():
                    print(f"Аккаунт {session_file} не авторизован. Попытка авторизации...")
                    phone_number = os.path.basename(session_file).replace('.session', '')
                    try:
                        await client.send_code_request(phone_number)
                        code = input(f"Введите код для аккаунта {phone_number}: ")
                        await client.sign_in(phone_number, code=code)
                        print(f"Аккаунт {session_file} успешно авторизован.")
                    except Exception as auth_error:
                        print(f"Ошибка при авторизации аккаунта {session_file}: {auth_error}")
                        print(f"Удаление недействительного аккаунта {session_file}...")
                        await client.disconnect()
                        os.remove(session_file)
                        print(f"Аккаунт {session_file} удален.")
                        continue  # Перейти к следующему аккаунту

                # Получаем дату 30 дней назад
                date_limit = datetime.now() - timedelta(days=30)
                unique_usernames = set()  # Используем set для хранения уникальных username

                # Перебираем сообщения в чате
                async for message in client.iter_messages(chat_url, offset_date=date_limit):
                    if message.sender and message.sender.username:
                        username = message.sender.username
                        if username not in unique_usernames:  # Проверяем уникальность
                            f.write(username + "\n")  # Записываем имя пользователя
                            unique_usernames.add(username)  # Добавляем в set

                print(f"Чат спарсен с использованием аккаунта {i + 1}")

            except Exception as e:
                print(f"Ошибка при парсинге с аккаунта {i + 1}: {e}")

            finally:
                await client.disconnect()

    print(f"Парсинг завершен. Результаты сохранены в {output_file}")


async def check_and_auth_accounts():
    """Проверяет и авторизует аккаунты."""
    accounts = load_accounts()
    for account_session in accounts:
        client = TelegramClient(account_session, API_ID, API_HASH)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"Аккаунт {account_session} не авторизован.  Пожалуйста, авторизуйте аккаунт.")
                phone_number = os.path.basename(account_session).replace('.session', '')
                await client.send_code_request(phone_number)
                code = input(f'Введите код для аккаунта {phone_number}: ')
                await client.sign_in(phone_number, code=code)
                print(f"Аккаунт {account_session} успешно авторизован.")
            await client.disconnect()
        except Exception as e:
            print(f"Ошибка при проверке аккаунта {account_session}: {e}")
            try:
                await client.disconnect()
            except:
                pass


if __name__ == '__main__':
    if not os.path.exists(ACCOUNTS_DIR):
        os.makedirs(ACCOUNTS_DIR)

    async def main():
        await check_and_auth_accounts()
        while True:
            print("\nТелеграм создателя https://t.me/assanof1:")
            print("\nВыберите ниже")
            print("1. Добавить аккаунт")
            print("2. Список аккаунтов")
            print("3. Инвайт пользователей")
            print("4. Парсинг чата")
            print("5. Выход")
            choice = input("Ваш выбор: ")
            if choice == '1':
                await add_account()
            elif choice == '2':
                list_accounts()
            elif choice == '3':
                accounts = load_accounts()
                users_file = input("Введите путь к файлу с username: ")
                num_accounts_to_use = int(input("Сколько аккаунтов использовать: "))
                num_invites = int(input("Сколько инвайтов сделать: "))
                chat_url = input("Введите URL чата: ")
                delay = int(input("Введите задержку (сек): "))
                await invite_users(accounts, users_file, num_accounts_to_use, num_invites, chat_url, delay)
            elif choice == '4':
                chat_url = input("Введите URL чата для парсинга: ")
                num_accounts = int(input("Сколько аккаунтов использовать для парсинга: "))
                await (chat_url, num_accounts)
            elif choice == '5':
                print("Выход.")
                break
            else:
                print("Некорректный выбор.")


    asyncio.run(main())
