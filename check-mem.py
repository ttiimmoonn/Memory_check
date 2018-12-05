#!/usr/bin/env python3
import psutil
from  datetime import datetime
from subprocess import check_output
import time
import os
import signal
import sys
import argparse
import re
import logging 


#создаем логгер
def create_logger(log_path):
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	 
	handler = logging.StreamHandler()
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)-8s %(levelname)-8s [%(module)s:%(lineno)d] %(message)-8s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	handler = logging.FileHandler("{}/check_mem_error.log".format(log_path),"w", encoding=None, delay="true")
	handler.setLevel(logging.ERROR)
	formatter = logging.Formatter("%(asctime)-8s %(levelname)-8s [%(module)s:%(lineno)d] %(message)-8s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	handler = logging.FileHandler("{}/check_mem_all.log".format(log_path),"w")
	handler.setLevel(logging.DEBUG)
	formatter = logging.Formatter("%(asctime)-8s %(levelname)-8s [%(module)s:%(lineno)d] %(message)-8s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	return(logger)

#парсим аргументы 
def create_parser():
	new_parser = argparse.ArgumentParser()
	new_parser.add_argument('-p', '--pid', type=str, required=False)
	new_parser.add_argument('-n', '--name_proc', type=str, required=False)
	new_parser.add_argument('-t', '--timeout', type=str, required=False)
	new_parser.add_argument('-e', '--error', type=int, required=False)
	return new_parser

#ищем pid процесса по его имени
def get_pid(name):
	try:
		numberBy = check_output(["pidof", "-s", name])
		res = numberBy.decode('utf-8')
		return (res[:-1:])
	except Exception as ex:
		logger.error("Error check pid...")
		logger.debug(ex)
		return False

#считаем результат
def check_resul(initial_result, final_result):
	try:
		result_result = {}
		for a in initial_result.keys():
			result_result[a] = final_result[a] - initial_result[a]
		logger.info("{}--| [ {} ] rss {}  uss {} pss {}".format(result_result["time"], "result",  result_result["rss"], result_result["uss"], result_result["pss"]))
		return(result_result)
	except Exception as ex:
		logger.error("Error check result...")
		logger.debug(ex)
		return False

#при получении сигнала завершения, пакуем результат в лог файл
def signal_handler(current_signal, frame):
	if csv:
		csv.close()
	if check_resul(initial_result, final_result):	
		if error < check_resul(initial_result, final_result)["rss"]:
			logger.error("{}--| Flew out of range... False", )
			sys.exit(1)
		else:
			logger.info("  --| Test Succ.")
			sys.exit(1)
	else:
		logger.error("{}--| Error check_resul...")
		sys.exit(1)

#чекаем память
def memr_stat(pid_pr, csv_path, start_time):
	try:
		time_now = datetime.strftime(datetime.now(), "%H_%M_%S")
		pr = psutil.Process(int(pid_pr)) 
		a = pr.memory_full_info()

		logger.info("{}--| [ {} ] rss {} vms {} shared {} text {} data {} uss {} pss {}".format(time_now, pr.name(), a[0], a[1], a[2], a[3], a[5], a[7], a[8]))
		with open("{}/check_mem_{}_csv.csv".format(csv_path, start_time), "a+") as csv:
			csv.write("{};{};{};{};{};{};{};{};\n".format(time_now, a[0], a[1], a[2], a[3], a[5], a[7], a[8]))
		return({"time": datetime.now(), "rss": a[0], "uss": a[7],"pss": a[8]})
	except Exception as ex:
		logger.error("Error reading parameters..")
		logger.debug("%s", ex)
		sys.exit(1)

try:
	#объявляем время старта утилиьы
	start_time = datetime.strftime(datetime.now(), "%Y_%m_%d_%H_%M_%S")

	#начинаем ловить сигналы
	signal.signal(signal.SIGINT, signal_handler)

	#получаем пути к логу
	log_path = "/var/log/apps/check_mem/{}".format(start_time)
	csv_path = log_path + "/csv"

	#создали пути для лога и csv файла
	os.makedirs(log_path)
	os.makedirs(csv_path)

	#пилим логгер
	logger = create_logger(log_path)
	#пилим  csv файл
	csv = open("{}/check_mem_{}_csv.csv".format(csv_path, start_time), "w+")
	csv.write("pidPR\ntime;rss;vms;shared;text;data;uss;pss;\n")
	csv.close()

	#парсим аргументы
	arg_parser = create_parser()
	namespace = arg_parser.parse_args()

	#определяем таймер между измерениями
	if namespace.timeout:
		timeout = int(namespace.timeout)
	else:
		timeout = 1

	logger.info("Timeoute installed [ %s s ]", timeout)

	#определяем допустиму погрешность в битах
	if namespace.error:
		error = namespace.error
	else:
		error = 10

	logger.info("Maximum error of [ %s bits ]", error)

	#определяем pid за которым будем следить
	if namespace.pid:
		pid_pr = namespace.pid
		logger.info("Pid is defined by the -p tag: [ %s ]", pid_pr)
	elif namespace.name_proc:
		pid_pr = get_pid(str(namespace.name_proc))
		logger.info("Pid is defined by the -n tag: [ %s ]", pid_pr)
	else:
		logger.error("No arguments specified...")
		sys.exit(1)

	#определили первый result
	initial_result = memr_stat(pid_pr, csv_path, start_time)

	while True:
		final_result = memr_stat(pid_pr, csv_path, start_time)	
		time.sleep(timeout)

except Exception as ex:
	logger.error("Error proc..")
	logger.debug("%s", ex)
	sys.exit(1)