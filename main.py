import xmltodict
import os
import json
import click
import csv 


def xml_to_json(path: str):
    with open(path, 'r') as file:
        my_dict = xmltodict.parse(file.read())
        return my_dict


def csv_to_json(csv_path: str):
    csvList = []
    with open(csv_path) as csv_file:
        csvReader = csv.DictReader(csv_file)
        for row in csvReader:
            csvList.append(row)
        return csvList

if __name__ == "__main__":
    csv_path = click.prompt('Path or name of the csv file ')
    csv_json = csv_to_json(csv_path)
    path = click.prompt('Path or name of the xml file ')
    xml_json = xml_to_json(path)
    print(type(xml_json),type(csv_json))
    