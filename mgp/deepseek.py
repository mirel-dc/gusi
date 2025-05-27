import requests
import json

API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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"
]
MODEL = "deepseek/deepseek-r1"
API_KEY = ""

def process_content(content):
    return content.replace('<think>', '').replace('</think>', '')

def chat_stream(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    with requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        stream=True
    ) as response:
        if response.status_code != 200:
            print("Ошибка API:", response.status_code)
            return ""

        full_response = []
        
        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode('utf-8').replace('data: ', '')
                try:
                    chunk_json = json.loads(chunk_str)
                    if "choices" in chunk_json:
                        content = chunk_json["choices"][0]["delta"].get("content", "")
                        if content:
                            cleaned = process_content(content)
                            print(cleaned, end='', flush=True)
                            full_response.append(cleaned)
                except:
                    pass

        print()  # Перенос строки после завершения потока
        return ''.join(full_response)


def process_content(content):
    return content.replace('<think>', '').replace('</think>', '')


def chat_stream(prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    try:
        with requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                stream=True
        ) as response:
            if response.status_code != 200:
                print(f"Ошибка API: {response.status_code} - {response.text}")
                return ""

            full_response = []

            for chunk in response.iter_lines():
                if chunk:
                    chunk_str = chunk.decode('utf-8').strip()
                    if chunk_str.startswith('data: '):
                        chunk_str = chunk_str[6:]

                    if chunk_str == '[DONE]':
                        continue

                    try:
                        chunk_json = json.loads(chunk_str)
                        if "choices" in chunk_json and chunk_json["choices"]:
                            content = chunk_json["choices"][0]["delta"].get("content", "")
                            if content:
                                cleaned = process_content(content)
                                print(cleaned, end='', flush=True)
                                full_response.append(cleaned)
                    except json.JSONDecodeError:
                        pass

            print()  # Перенос строки после завершения потока
            return ''.join(full_response)

    except Exception as e:
        print(f"Произошла ошибка при выполнении запроса: {str(e)}")
        return ""


def main():
    print("Чат с DeepSeek-R1\nДля выхода введите 'exit'\n")

    while True:
        try:
            choice = int(input(f"Выберите ключ (1-{len(API_KEYS)}): ")) - 1
            if 0 <= choice < len(API_KEYS):
                api_key = API_KEYS[choice]
                print(f"Выбран ключ #{choice + 1}")
            else:
                print("Нужно ввести число от 1 до 29")
                continue

            while True:
                user_input = input("\nВы: ")

                if user_input.lower() == 'exit':
                    print("Завершение работы...")
                    return

                if not user_input.strip():
                    print("Сообщение не может быть пустым")
                    continue

                print("DeepSeek-R1:", end=' ', flush=True)
                chat_stream(user_input, api_key)

        except ValueError:
            print("Пожалуйста, введите число")
        except KeyboardInterrupt:
            print("\nЗавершение работы...")
            return
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()