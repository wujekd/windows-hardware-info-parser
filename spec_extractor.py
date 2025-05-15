#!/usr/bin/env python3
import os
import glob
import re
import csv

def parse_msinfo(path):
    idx_map = {
        'CPU':          29,
        'Board Make':   39,
        'Board Model':  41,
        'Board Version':43,
        'BIOS_Mode':    37,
        'Secure_Boot':  47,
        'RAM':          65,
    }
    
    data = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    for key, idx in idx_map.items():
        line = lines[idx - 1]
        parts = line.split("\t", 1)
        info = parts[1].strip()
        data[key] = info
    
    return data
    
def parse_dxdiag(path):
    data = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith('DirectX Version:'):
                data['DirectX_Version'] = line.split(':',1)[1].strip()
            elif line.startswith('Driver Model:'):
                data['Driver_Model'] = line.split(':',1)[1].strip()
            elif line.startswith('Card name:'):
                data['GPU'] = line.split(':',1)[1].strip()
    return data

def main():
    msinfo_files = glob.glob('*_msinfo32.txt') # get all msinfo32 files
    if not msinfo_files:
        print("Not a single msinfo32 file here. Come on mate, wyd.")
        return

    output_csv = 'all_machines_specs.csv'
    fields = [
        'Machine_Number','ID',
        'CPU','RAM',
        'Board Make','Board Model','Board Version',
        'BIOS_Mode','Secure_Boot',
        'DirectX_Version','Driver_Model','GPU'
    ]
    with open(output_csv, 'w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()

        for msfile in msinfo_files:
            base = os.path.splitext(msfile)[0]  # split extension from file name
            parts = base.split('_')
            if len(parts) < 3:
                print(f"bad file name (not number_id_msinfo32): {msfile}")
                continue
            machine_num, comp_id = parts[0], parts[1]

            ms_data = parse_msinfo(msfile)

            dxfile = f"{machine_num}_{comp_id}_dxdiag.txt"
            dx_data = {}
            if os.path.exists(dxfile):
                dx_data = parse_dxdiag(dxfile)
            else:
                print(f"{dxfile} not found, skipping dx data")

            row = {
                'Machine_Number': machine_num,
                'ID':    comp_id,
                'CPU':            ms_data.get('CPU',''),
                'RAM':            ms_data.get('RAM',''),
                'Board Make':     ms_data.get('Board Make'),
                'Board Model':    ms_data.get('Board Model'),
                'Board Version':  ms_data.get("Board Version"),
                'BIOS_Mode':      ms_data.get('BIOS_Mode',''),
                'Secure_Boot':    ms_data.get('Secure_Boot',''),
                'DirectX_Version': dx_data.get('DirectX_Version',''),
                'Driver_Model':    dx_data.get('Driver_Model',''),
                'GPU':             dx_data.get('GPU',''),
            }
            writer.writerow(row)
    print('Alright then. It worked.')

if __name__ == '__main__':
    main()