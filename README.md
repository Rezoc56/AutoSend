# AutoSend

Стабильная версия — **1.5**

## Что нового в 1.5

* Добавлен режим отправки «По очереди»: каждая строка текста отправляется отдельным нажатием активации, после последней строки отправка начинается заново.
* Добавлена глобальная горячая клавиша **F8** для запуска и остановки, работает даже когда окно программы не в фокусе.
* Добавлен счётчик отправок в нижней панели.
* Счётчик символов теперь показывает и количество непустых строк.
* Добавлена опция «Случайность задержки» (разброс ±30%), чтобы отправка выглядела естественнее.
* Добавлена опция «Поверх всех окон».
* Настройки теперь хранятся в формате JSON и сохраняют все новые параметры между запусками; старый файл `settings.txt` подхватывается автоматически.
* Исправлена потеря многострочного текста при загрузке настроек.
* Исправлено зависание обработчика клавиатуры во время задержки: отправка теперь выполняется в отдельном потоке и защищена от повторных срабатываний.
* Исправлено отображение надписи «Нажмите клавишу...» при выборе клавиши активации.
* Запуск с пустым текстом теперь блокируется с предупреждением.
* Остановка программы снимает только собственные перехватчики клавиатуры, не затрагивая глобальную горячую клавишу.
* Оптимизирован код интерфейса и обновлён дизайн: единые стили кнопок с подсветкой при наведении, улучшенные отступы и переключатели.

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

Stable version — **1.5**

## What's New in Version 1.5

* Added the "Sequential" sending mode: each line of text is sent on a separate activation key press, looping back to the first line after the last one.
* Added the global **F8** hotkey for starting and stopping, which works even when the program window is not in focus.
* Added a sent messages counter to the bottom bar.
* The character counter now also shows the number of non-empty lines.
* Added the "Randomize delay" option (±30% variation) to make sending look more natural.
* Added the "Always on top" option.
* Settings are now stored in JSON format and keep all new options between sessions; the old `settings.txt` file is imported automatically.
* Fixed loss of multi-line text when loading settings.
* Fixed the keyboard handler freezing during the delay: sending now runs in a separate thread and is protected against repeated triggers.
* Fixed the display of the "Press a key..." label when selecting the activation key.
* Starting with empty text is now blocked with a warning.
* Stopping the program now removes only its own keyboard hooks, leaving the global hotkey intact.
* Optimized the interface code and updated the design: unified button styles with hover highlighting, improved spacing, and toggles.

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
