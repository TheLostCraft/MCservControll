import requests
import os

FILES_TO_UPDATE = {
    "main.py": "https://raw.githubusercontent.com/TheLostCraft/MCservControll/main/bot/main.py",
    "func.py": "https://raw.githubusercontent.com/TheLostCraft/MCservControll/main/bot/func.py"
}

def update_file(filename, url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        file_path = os.path.join(".", filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"[INFO] {filename} has been successfully updated.")
    except Exception as e:
        print(f"[ERROR]: {filename}: could not update: {e}")

def main():
    for filename, url in FILES_TO_UPDATE.items():
        update_file(filename, url)

    print("[INFO] All files were checked and updated where necessary.")

if __name__ == __name__:
    main()
