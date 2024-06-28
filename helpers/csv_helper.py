import csv
import os

def get_data_from_csv(file_path):
	data = []

	try:
		with open(file_path, encoding="UTF-8-SIG") as csv_file:
			csv_dictionary = csv.DictReader(csv_file, delimiter=',')

			for dictionary_row in csv_dictionary:
				data.append(dictionary_row)
	except:
		print('File was not found in csvs' + file_path)
		exit()

	return data
