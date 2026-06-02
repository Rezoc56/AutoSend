# AutoSend

Стабильная версия — **1.4**

## Что нового в 1.4

* Добавлен счётчик символов в реальном времени (подсвечивается оранжевым при количестве символов более 500).
* Добавлена настраиваемая задержка перед отправкой (слайдер от 0 до 5 секунд).
* Добавлен режим отправки:

  * Вставка + Enter;
  * Только вставка.
* Добавлен статусбар с цветовой индикацией состояния программы:

  * Серый — остановлено;
  * Зелёный — активно.
* Добавлена горячая клавиша **Ctrl+Enter** для быстрого запуска и остановки.
* Расширено контекстное меню: добавлены пункты «Вырезать», «Отменить» и «Повторить».
* Проверка обновлений перенесена в отдельный поток и больше не замедляет запуск программы.
* Настройки теперь сохраняют выбранную задержку и режим отправки между запусками.
* Обновлён дизайн интерфейса.

## Функционал

AutoSend — простая программа для автоматической вставки и отправки текста. Это моя первая опубликованная программа.

Принцип работы:

1. Введите необходимый текст.
2. Выберите клавишу активации.
3. Запустите программу.
4. Нажмите выбранную клавишу в любом приложении, где доступен ввод текста.

После нажатия выбранной клавиши программа автоматически вставит заранее подготовленный текст.

Если в качестве клавиши активации выбрать **Enter**, сообщение будет автоматически отправляться сразу после вставки текста. Клавишу также можно удерживать для многократного срабатывания.

## Информация, которая может быть полезна

* Программа может работать без подключения к интернету.
* Интернет используется только для проверки наличия обновлений.
* Для сохранения настроек программа создаёт файл:

`C:\Users\Имя Пользователя\AppData\Roaming\Rezoc Studio\AutoSend\settings.txt`

В данном файле сохраняются:

* выбранная клавиша активации;
* введённый текст;
* задержка перед отправкой;
* режим отправки.

Благодаря этому настройки не требуется вводить заново после каждого запуска программы.

## Установка (простая)

1. Скачайте архив или готовый исполняемый файл AutoSend.exe.
2. Запустите программу.

## Установка (из исходного кода)

### Требования

* Python 3.10 или новее.
* Библиотеки:

  * requests
  * keyboard

### Установка зависимостей

```bash
pip install requests keyboard
```

### Запуск программы

```bash
python AutoSend.py
```

### Сборка в EXE (необязательно)

При необходимости программу можно самостоятельно скомпилировать в исполняемый файл:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed AutoSend.py
```

После завершения сборки готовый файл будет находиться в папке `dist`.


# AutoSend

Stable version — **1.4**

## What's New in Version 1.4

* Added a real-time character counter (highlighted in orange when the text exceeds 500 characters).
* Added a configurable delay before sending (0–5 second slider).
* Added sending modes:

  * Paste + Enter;
  * Paste Only.
* Added a status bar with color indication:

  * Gray — stopped;
  * Green — active.
* Added the **Ctrl+Enter** hotkey for quick start and stop.
* Expanded the context menu with Cut, Undo, and Redo actions.
* Update checking now runs in a background thread and no longer delays program startup.
* Settings now save the selected delay and sending mode between sessions.
* Updated user interface design.

## Features

AutoSend is a simple utility for automatic text insertion and sending. It is my first publicly released software project.

How it works:

1. Enter the desired text.
2. Select an activation key.
3. Start the program.
4. Press the selected key in any application where text input is available.

The program will automatically insert the predefined text.

If **Enter** is selected as the activation key, the message will be automatically sent immediately after insertion. The activation key can also be held down for repeated activation.

## Additional Information

* The program can work without an internet connection.
* Internet access is only used to check for software updates.
* The program creates the following file:

`C:\Users\Username\AppData\Roaming\Rezoc Studio\AutoSend\settings.txt`

This file stores:

* the selected activation key;
* the entered text;
* the sending delay;
* the sending mode.

This allows the program to restore settings automatically on the next launch.

## Installation (Easy)

1. Download the archive or the prebuilt AutoSend.exe file.
2. Run the program.

## Installation (From Source Code)

### Requirements

* Python 3.10 or newer.
* Required libraries:

  * requests
  * keyboard

### Installing Dependencies

```bash
pip install requests keyboard
```

### Running the Program

```bash
python AutoSend.py
```

### Building an EXE File (Optional)

You can compile the application into a standalone executable file:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed AutoSend.py
```

After compilation, the executable file will be located in the `dist` folder.
