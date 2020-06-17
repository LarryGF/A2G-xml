import xmltodict
import os
import json
import click
import csv 
import glob

def xml_to_json(path: str):
    with open(path, 'r') as file:
        my_dict = xmltodict.parse(file.read())
        if my_dict.setdefault('OMeS', False):
            if my_dict['OMeS'].setdefault('PMSetup', False):
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

def adapt_json_to_csv(list_to_adapt:dict):
    big_list = []
    for measurement in list_to_adapt:
        if type(measurement['MO']) == list:
            MO_keys = list(measurement['MO'][0].keys())
            MO_keys = []
            temp_list = []
            for index,value in enumerate(measurement['MO']):
                temp_list.append(list(value.values()))
        
            len_temp_list = len(temp_list)
            len_inner_lists = len(temp_list[0])
            count1 = 0
            count2 = 0
            final_list = []
            while count1 < len_inner_lists:
                small_list = []
                while count2 < len_temp_list:
                    small_list.append(temp_list[count2][count1])
                    count2+=1
                final_list.append(small_list)
                count1+=1
                count2=0
            
            MO_values = [tuple(element) for element in final_list]
           
            
           
        else:
            MO_keys = list(measurement['MO'].keys())
            MO_values = list(measurement['MO'].values())
        
        new_MO_keys = []
        for key in MO_keys:
            if '@' in key:
                new_MO_keys.append(key.replace('@',''))
            else:
                new_MO_keys.append(key)
        
        MO_keys = new_MO_keys
        
        Net_keys = list(measurement['NE-WBTS_1.0'].keys())
        
        new_Net_keys = []
        for key in Net_keys:
            if '@' in key:
                new_Net_keys.append(key.replace('@',''))
            else:
                new_Net_keys.append(key)
        Net_keys = new_Net_keys
        Net_values = list(measurement['NE-WBTS_1.0'].values())
        column_list =  MO_keys + Net_keys 
        values_list =  MO_values + Net_values
        big_list.append(column_list)
        big_list.append(values_list)
        big_list.append('')
    
    return big_list
        
if __name__ == "__main__":
    csv_path = click.prompt('Path or name of the csv file ',default='2.csv')
    csv_json = csv_to_json(csv_path)
    path = click.prompt('Path or name of the folder containing the xml files',default='xml')
    file_list = []
    os.chdir(path)
    for file in glob.glob("*.xml"):
        file_list.append(os.path.join(path,file))
    os.chdir('../')
    for new_path in file_list:
        
        
        xml_json = xml_to_json(new_path)
        # with open('xml.json','w') as file:
        #     json.dump(xml_json,file, indent=2)
        # with open('csv.json','w') as file:
        #     json.dump(csv_json,file, indent=2)
        
        processed_xml_json = process_xml_json(xml_json,csv_json)
        with open('processed_xml.json','w') as file:
            json.dump(processed_xml_json,file, indent=2)
            
        count10 = 0
        for date in processed_xml_json:
            list_to_adapt = processed_xml_json[date]
            list_of_lists = adapt_json_to_csv(list_to_adapt)
            new_date = date.replace('-','_').replace(':','-')
            
            with open(new_date+'.csv','w', newline='') as file:
                writer =  csv.writer(file)
                writer.writerows(list_of_lists)
            count10+=1