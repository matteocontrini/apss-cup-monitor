import html
import json
import os
from hashlib import md5

import requests


def main():
    token = login()
    payload = fetch_availabilities(token)

    output = f'''
Providers: <code>{html.escape(str(payload['providers']))}</code>
Providers2: <code>{html.escape(str(payload['providersToCompare']))}</code>
Warnings: <code>{html.escape(str(payload['warnings']))}</code>
'''.strip()

    print(output)

    telegram(output)


def login():
    url = 'https://cup.apss.tn.it/mobile/v2/authentication'
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    password_md5 = md5(password.encode('utf-8')).hexdigest()
    data = {
        'contextID': 'APSS',
        'username': username,
        'deviceSerialNumber': '0',
        'cordovaVersion': '0',
        'model': 'Firefox',
        'platform': 'Browser',
        'platformVersion': 'Mac OS 10.15',
        'appVersion': '020912',
        'password': password_md5,
        'passwordDecrypted': password
    }

    res = requests.post(
        url,
        json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    payload = res.json()
    token = payload['token']
    return token


def fetch_availabilities(token: str):
    url = 'https://cup.apss.tn.it/mobile/search-resources'
    data = {"startDate": "2025-02-25T23:00:00.000Z", "type": 1, "maxDistance": 180, "searchNear": False,
            "personFiscalCode": os.environ['USERNAME'].upper(), "searchSynchro": False, "sameDiary": False,
            "weekdays": "1111111",
            "hours": "111111111111", "idExams": [
            {"code": "5000902", "encodingSystem": "APSS_SCHIARA", "flagRepeatable": False, "familyCode": "",
             "bookable": False, "publicAccess": False, "directAccess": False, "aliases": ["LARINGOSCOPIA", "31.42.2"],
             "regimes": [{"regimeName": "SSN", "bookable": True}], "flagValid": False, "familyName": ""}],
            "paymentSubject": "SSN", "priorityCode": "NPR", "language": "it", "maxResults": 200}
    res = requests.post(
        url,
        json.dumps(data),
        headers={'Content-Type': 'application/json', 'token': token}
    )
    return res.json()


def telegram(output: str):
    url = 'https://api.telegram.org/bot' + os.environ['BOT_TOKEN'] + '/sendMessage'
    data = {
        'chat_id': os.environ['CHAT_ID'],
        'text': output,
        'parse_mode': 'HTML'
    }
    res = requests.post(url, json.dumps(data), headers={'Content-Type': 'application/json'})
    if res.status_code != 200:
        print(res.status_code)
        print(res.text)
        raise Exception('Telegram error')


if __name__ == '__main__':
    main()
