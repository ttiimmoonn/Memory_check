<h1> Memory check </h1>
Python 3.5. or greater
Modules are required: psutil.

<h2> [ru] </h2>
Утилита измеряющая оперативную память, занимаемую определенным процессом.
<h3> Файловая структура </h3>
Этот скрипт использует для запуска файл:
<li> check-mem.py </li>
И файлы для результата:
<li> check_mem_error.log </li>
<li> check_mem_all.log </li>
<h4> check_mem_{data}_csv.csv </h4>
Файлы с результатами хранятся по пути: <code>/var/log/apps/check_mem</code>. 

<h3>Для запуска скрипта используются ключи:</h3>
<li> <code> -h </code>, <code> - help </code> Показывает помощь и выходит. </li>
<li> <code> -p </code>, <code> - pid </code> Строго указать pid процесса.</li>
<li> <code> -n </code>, <code> - name_proc </code> Искать pid по указанному имени. </li>
<li> <code> -t </code>, <code> - timeout </code> Указывает перерыв в секундах между измерениями (по умолчанию 1). </li>
<li> <code> -e </code>, <code> - error </code> Указывает максимально допустимую ошибку в битах (по умолчанию 8000). </li>
