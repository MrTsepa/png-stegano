# Стеганография
Главный принцип стеганографии состоит в том, чтобы скрыть конфиденциальную информацию внутри открытой. Один тип информации (в нашем случае какой-либо текст) помещается внутрь другой информации (изображения PNG). Тем самым это позволяет передавать секретную информацию через открытые каналы, скрывая сам факт её передачи. Разница между пустым и заполненным контейнером (информация, которая таит в себе стегосообщение) не ощутима для органов восприятия человека.

# Описание проекта
В данном проекте использовалась одна из особенностей PNG файлов - фильтрация строк (scanline filtering, или delta filters), благодаря которой PNG-упаковщик может получить гораздо более удобные данные для сжатия. Основная идея состоит в том, что мы можем менять фильтр вручную. Для этого нужно декодировать строку из существующего фильтра и закодировать с новым фильтром. Именно в байтах фильтра и будет храниться информация. При этом информация изображения не теряется, а просто предстает в другом формате.

# Файлы проекта
Название файла           | Содержание файла
-------------------------|----------------------
gui_zero.py              | Простой GUI
png_stegano.py           | Несколько классов для разных методов стеганографии
filter_utils.py          | Вспомогательные функции для кодирования и декодирвания при помощи фильтров PNG
png_utils.py             | Вспомогательные функции для работы с чанками PNG

# Примеры
![eee7](https://user-images.githubusercontent.com/17471115/34066036-152c6794-e21a-11e7-9b75-d9944900a441.jpg)

![eee1](https://user-images.githubusercontent.com/17471115/34066045-2d33fb40-e21a-11e7-8f15-fa72aa84f098.jpg)

![eee5](https://user-images.githubusercontent.com/17471115/34066037-16d838fc-e21a-11e7-88b1-139a62017fc5.jpg)
