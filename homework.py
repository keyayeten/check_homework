import telegram
import requests
import time
import os
from dotenv import load_dotenv
import logging
import sys


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TELEGA')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    level=logging.DEBUG,
    filename='bot_logs.log',
    filemode='w'
)

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Checking availability of all tokens"""
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        print('Не удалось получить все необходимые переменные окружения.')
        return False
    return True


def send_message(bot, message):
    bot.send


def get_api_answer(timestamp):
    payload = {'from_date': timestamp}
    responce = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    if responce == '<Response [200]>':
        return responce.json()



def check_response(response):
    if type(response) == dict:
        if type(response.get('homeworks')) == list:
            return response.get('homeworks')[0]
        elif type(response.get('homeworks')) != list:
            raise TypeError('Ключ homework не список!')
    else:
        raise TypeError('Получен список вместо ожидаемого словаря')


def parse_status(homework):
    homework_name = homework[0]['homework_name']
    verdict = HOMEWORK_VERDICTS[homework[0]['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    if not check_tokens():
        logging.critical('Не хватает токенов')
        sys.exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    fromdate = timestamp - RETRY_PERIOD

    while True:
        try:
            response = get_api_answer(fromdate)
            check_response(response)
            homeworks = response['homeworks']
            if homeworks:
                homework = homeworks[0]
                status = parse_status(homework)
                send_message(bot, status)
            fromdate = response['current_date']
            time.sleep(RETRY_PERIOD)


        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)


if __name__ == '__main__':
    main()
