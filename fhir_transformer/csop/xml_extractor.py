import encodings
import xmltodict
import sys
import re

license_mapping = {
    'ว': {
        'type': 'MD',
        'system': 'https://www.tmc.or.th'
    },
    'ท': {
        'type': 'DDS',
        'system': 'https://www.dentalcouncil.or.th'
    },
    'พ': {
        'type': 'NP',
        'system': 'https://www.tnmc.or.th'
    },
    'ภ': {
        'type': 'RPH',
        'system': 'https://www.pharmacycouncil.org'
    },
    '-': {
        'type': 'Other', ### เพิ่มเติมในกลุ่มอื่น ๆ
        'system' : '-'
    },
    'N': {
        'type': 'No data', ### ดักกรณีไม่มีค่า
        'system' : '-'
    }
}

def _get_file_encoding(file_path):
    with open(file_path,'rb') as xml_file_for_encoding_check:
        first_line = xml_file_for_encoding_check.readline().decode("utf-8") 
        encoding = re.search('encoding="(.*)"', first_line).group(1)
        if encoding == "windows-874":
            encoding = "cp874"
        return encoding

def _open_bill_trans_xml(file_path: str):
    tran_items = dict()
    with open(file_path, encoding=_get_file_encoding(file_path)) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        h_code = data_dict['ClaimRec']['Header']['HCODE']
        h_name = data_dict['ClaimRec']['Header']['HNAME']
        bill_trans = data_dict['ClaimRec']['BILLTRAN'].split('\n')
        bill_trans_items = data_dict['ClaimRec']['BillItems'].split('\n')
        for item in bill_trans:
            item_split = item.split('|')

            for i in range(len(item_split)):
                if item_split[i] == '':
                    item_split[i] = 'None'
            
            item_data = {
                'station': item_split[0],
                'inv_no': item_split[4],
                'hn': item_split[6],
                'member_no': item_split[7],
                'pid': item_split[12],""
                'name': item_split[13],
                'pay_plan': item_split[15],
                'bill_items' : list()
            }
            tran_items[item_data['inv_no']] = item_data
    return tran_items,h_code,h_name
def _open_bill_disp_xml(file_path: str):
    disp_items = dict()
    with open(file_path, encoding=_get_file_encoding(file_path)) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        main_disps = data_dict['ClaimRec']['Dispensing'].split('\n')
        detail_disps = data_dict['ClaimRec']['DispensedItems'].split('\n')
        for item in main_disps:
            item_split = item.split('|')
            
            for i in range(len(item_split)):
                if item_split[i] == '' or item_split[i] == None:
                    item_split[i] = 'None'
            item_data = {
                'provider_id': item_split[0],
                'disp_id':item_split[1],
                'inv_no': item_split[2],
                'presc_date': item_split[5]+"+07:00",
                'disp_date': item_split[6]+"+07:00",
                'license_id': item_split[7],
                'disp_status': item_split[15],
                'practitioner': license_mapping[item_split[7][0]],
                'items': list()
            }
            disp_items[item_data['disp_id']] = item_data
        for item in detail_disps:
            item_split = item.split('|')

            for i in range(len(item_split)):
                if item_split[i] == '':
                    item_split[i] = 'None'

            item_details_data = {
                'disp_id':item_split[0],
                'product_cat': item_split[1],
                'local_drug_id': item_split[2],
                'standard_drug_id': item_split[3],
                'dfs': item_split[5],
                'package_size': item_split[6],
                'instruction_code': item_split[7],
                'instruction_text': item_split[8],
                'quantity': item_split[9]
            }
            current_items = disp_items[item_details_data['disp_id']]['items']
            current_items.append(item_details_data)
            disp_items[item_details_data['disp_id']]['items'] = current_items
    return disp_items