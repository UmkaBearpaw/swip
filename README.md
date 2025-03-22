# Simple Whisper Interface Panel (SWIP)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)

GUI приложение для преобразования аудио/видео в текст с помощью OpenAI Whisper.


## **1. Установка Python**
### Для Windows:
1. Скачайте Python 3.11 с [официального сайта](https://www.python.org/downloads/windows/).
2. Запустите установщик:
   - Отметьте **Add python.exe to PATH**.
   - Нажмите **Install Now**.

### Для Windows из консоли PowerShell+Chocolatey+Python:
1. Установка Chocolatey:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
2. Установка Python
```powershell
choco install python --version=3.12.4
```


### Для Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

### Для macOS:
1. Установите через [Homebrew](https://brew.sh/):
```bash
brew install python@3.11
```

---

## **2. Установка зависимостей**
### Для всех ОС:
1. Откройте терминал (CMD/PowerShell на Windows).
2. Установите `pip` (если не установлен):
```bash
python -m ensurepip --upgrade
```

3. Установите основные зависимости:
```bash
pip install -r requirements.txt
```

4. Установите PyTorch (выберите вариант для вашего железа):
- **Для CPU**:
  ```bash
  pip install torch==2.2.1
  ```
- **Для GPU (NVIDIA)**:
  ```bash
  pip install torch==2.2.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```

---

## **3. Установка FFmpeg**
### Для Windows:
1. Скачайте [FFmpeg для Windows](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z).
2. Распакуйте архив в `C:\ffmpeg`.
3. Добавьте путь `C:\ffmpeg\bin` в системную переменную **PATH**.

Подробная официальная [инструкция](https://www.wikihow.com/Install-FFmpeg-on-Windows) для установки FFmpeg.

### Для Linux (Ubuntu/Debian):
```bash
sudo apt install ffmpeg
```

### Для macOS:
```bash
brew install ffmpeg
```

---

## **4. Подготовка проекта**
1. Скопируйте [код приложения](https://gist.github.com/your-gist-link) в файл `app.py`.
2. Сохраните его в удобную папку (например, `C:\whisper_app`).

---

## **5. Запуск приложения**
1. Откройте терминал в папке с `app.py`.
2. Выполните команду:
```bash
python app.py
```

---

## **Готово!**  
После запуска откроется окно приложения:
1. Нажмите **Выбрать файл** и укажите видео/аудио.
2. Выберите модель (рекомендуется `turbo` для баланса скорости и качества).
3. Отметьте форматы сохранения (TXT/TSV).
4. При необходимости измените значение флага "Использовать GPU"
4. Нажмите **Старт**.

---

## **Дополнительные настройки**
### Виртуальное окружение (рекомендуется):
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Пример файла `requirements.txt`:
```
openai-whisper==20231117
torch==2.2.1
```

---

## **Возможные проблемы и решения**
1. **Ошибка с FFmpeg**:
   - Убедитесь, что FFmpeg добавлен в PATH.
   - Перезапустите терминал после установки.

2. **Недостаточно памяти**:
   - Используйте модели меньшие модели `small`, `tiny` или `base`.
   - Если используется GPU (флаг "Использовать GPU" включен), но видеопамяти не хватает, - отключите флаг. Конвертация будет производится с помощью CPU.
   - Закройте другие приложения.

3. **Ошибки с PyTorch**:
   - Переустановите PyTorch [по официальной инструкции](https://pytorch.org/).

---

Теперь вы можете конвертировать видео/аудио в текст в пару кликов! 🚀