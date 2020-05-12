import xmltodict
import os
import json
import click
import csv 


def xml_to_json(path: str):
    with open(path, 'r') as file:
        my_dict = xmltodict.parse(file.read())
    if my_dict.setdefault('OMeS', False):
        if my_dict['OMeS'].setdefault('PMSetup', False):
            print(len( my_dict['OMeS']['PMSetup']))
            data = my_dict['OMeS']['PMSetup']
            parsed_dict = {}
            for measurement in data:
                parsed_dict[measurement['@startTime']] = measurement['PMMOResult']
            return parsed_dict
        else:
            raise Exception('Script not prepaired for this structure')
    else:
        raise Exception('Script not prepaired for this structure')
def csv_to_json(csv_path: str):
    csvList = []
    csv_dict = {}
    with open(csv_path) as csv_file:
        csvReader = csv.DictReader(csv_file)
        for row in csvReader:
            csvList.append(row)
    
    for element in csvList:
        csv_dict[element["Counter ID"]] = {
            "Measurement ID and Name":element["Measurement ID and Name"],
            "Measurement ID and Name in release 19A":element["Measurement ID and Name in release 19A"],
            "Network Element Name":element["Network Element Name"],
             "Network Element Name in release 19A":element[ "Network Element Name in release 19A"]
        }
    return csv_dict

def process_xml_json(xml_json: dict,csv_json:dict):
    new_json = {}
    for date in xml_json:
        for dictio in xml_json[date]:
            if dictio.setdefault("NE-WBTS_1.0", False):
                for element in dict(dictio["NE-WBTS_1.0"]):
                    if element == '@measurementType':
                        pass
                    
                    else:
                        if element not in csv_json.keys():
                            print('Element',element, 'not present in the mapping dictionary')
                        else:
                            if csv_json[element]['Network Element Name in release 19A'] == '#N/A':
                                dictio["NE-WBTS_1.0"][csv_json[element]['Network Element Name']] = dictio["NE-WBTS_1.0"].pop(element)
                            else:
                                dictio["NE-WBTS_1.0"][csv_json[element]['Network Element Name in release 19A']] = dictio["NE-WBTS_1.0"].pop(element)
            else:
                raise Exception('Script not prepaired for this structure')
    return xml_json
if __name__ == "__main__":
    csv_path = click.prompt('Path or name of the csv file ',default='2.csv')
    csv_json = csv_to_json(csv_path)
    path = click.prompt('Path or name of the xml file ',default='1.xml')
    xml_json = xml_to_json(path)
    with open('xml.json','w') as file:
        json.dump(xml_json,file, indent=2)
    with open('csv.json','w') as file:
        json.dump(csv_json,file, indent=2)
    
    processed_xml_json = process_xml_json(xml_json,csv_json)
    with open('processed_xml.json','w') as file:
        json.dump(processed_xml_json,file, indent=2)