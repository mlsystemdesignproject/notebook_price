# Как запускать парсер цен ноутбуков МВидео
1) необходимо заполнить куки и заголовки в файле mvideo_config.py
 - 1.1 зайти на сайт https://www.mvideo.ru/noutbuki-planshety-komputery-8/noutbuki-118/f/category=noutbuki-987
 - 1.2 щелкнуть правой кнопкой мыши и выбрать "просмотреть код"
 - 1.3 выбрать вкладку "Network" и нажать на поле "Fetch/XHR"
 - 1.4 перезагрузить страницу
 - 1.5 в списке "Name" найти "list" и нажать правой кнопкой мыши
 - 1.6 нажать "copy" -> "Copy as cUrl (bash)"
 - 1.7 перейти на сайт https://curlconverter.com/python/ и вставить содержимое из буфера
 - 1.8 скопировать cookies и headers в соответствующие словари в файле mvideo_config.py 

**P.S.:** это последовательность действий описана для Google Chrome


2) Запустить скрипт main.py
