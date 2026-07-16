import json  # 맨 위에 추가
import requests
import os
import re

def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for MarkdownV2."""
    # List of all special characters that need to be escaped
    special_chars = r'_*[]()~`>#+-=|{}.!'
    # Escape each special character
    escaped_text = re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)
    return escaped_text

def send_message_md2(token: str, chat_id: int, text: str):
    """
    Sends a Telegram message formatted with MarkdownV2.
    NOTE: The input 'text' should be plain text. The function will escape it for MarkdownV2.
    To apply formatting, you must manually format the escaped text.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,  # Assuming the text is already correctly formatted/escaped
        "parse_mode": "MarkdownV2"
    }
    response = requests.post(url, json=payload)
    result = response.json()
    # 실패했을 경우 콘솔에 에러 원인 출력
    if not result.get("ok"):
        print(f"❌ Telegram API Error: {result.get('description')}")
        print(f"문제가 된 텍스트: {text}")

    return result

def send_telegram_message(token:str, chat_id, text:str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    return response.json()

def send_telegram_photo(token:str,chat_id:str,image_path:str,image_caption:str)->dict:
    url = f"https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}"
    payload = {
        "chat_id": chat_id,
        "caption": image_caption
    }
    filepath = os.path.join(os.path.abspath(os.getcwd()), image_path)
    response = requests.post(url, data=payload, files = {'photo':open(filepath, 'rb')})
    return response.json()


def send_doc(token:str,chat_id:str,path:str,caption:str)->dict:
    """
    Sends a transparent image as a document to one or more chat IDs.

    Args:
        token (str): Your Telegram Bot token.
        chat_id (list or str): A single chat ID or a list of chat IDs.
        path (str): The local file path to document (e.g., 'path/to/your/image.png').
        caption (str): An optional caption for the doc.

    Returns:
        dict: The JSON response from the Telegram API.
    """
    # Ensure chat_id is a list for consistent iteration
    if not isinstance(chat_id, list):
        chat_id = [chat_id]

    for cid in chat_id:
        # Change the API endpoint to sendDocument
        url = f"https://api.telegram.org/bot{token}/sendDocument"

        # Prepare the data payload
        data = {"chat_id": cid, "caption": caption}

        # Get the absolute file path
        filepath = os.path.join(os.path.abspath(os.getcwd()), path)

        # Open the file and send it
        # The key in the 'files' dictionary is 'document' for the sendDocument method
        with open(filepath, 'rb') as f:
            ret = requests.post(url, data=data, files={'document': f})

        # Return the JSON response for the last sent message
        return ret.json()

def send_media_group(token: str, chat_id: int, image_paths: list):
    """여러 장의 이미지를 텔레그램 앨범(Media Group)으로 묶어서 전송합니다."""
    url = f"https://api.telegram.org/bot{token}/sendMediaGroup"
    media = []
    files = {}

    for i, path in enumerate(image_paths):
        file_name = f"photo{i}"
        media.append({
            "type": "photo",
            "media": f"attach://{file_name}"
        })
        # 파일을 바이너리 읽기 모드로 엽니다
        files[file_name] = open(path, 'rb')

    payload = {"chat_id": chat_id, "media": json.dumps(media)}
    response = requests.post(url, data=payload, files=files)

    # 전송 후 열려있는 파일 객체들을 모두 닫아줍니다
    for f in files.values():
        f.close()

    return response.json()
