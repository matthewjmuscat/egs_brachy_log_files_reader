import os
import re
import csv

def find_log_files(base_path):
    patient_folders = [f for f in os.listdir(base_path) if re.match(r'PT\d{4}', f)]
    log_files = []
    for folder in patient_folders:
        tg43_path = os.path.join(base_path, folder, 'TG43', 'phantom')
        if os.path.exists(tg43_path):  # Check if TG43/phantom path exists
            folder_number = re.search(r'PT(\d{4})', folder).group(1)
            for file in os.listdir(tg43_path):
                if re.search(folder_number, file) and file.endswith('.log'):
                    log_files.append(os.path.join(tg43_path, file))
        else:
            print(f"Skipping {folder}: TG43/phantom directory does not exist.")
    return log_files

def extract_prostate_data(log_file_path):
    with open(log_file_path, 'r') as file:
        content = file.read()
    match = re.search(r'Structure voxel count:(.*?)(?:---|$)', content, re.DOTALL)
    if match:
        structures = match.group(1).strip()
        prostate_data = re.findall(r'(prostate[\w_]*\s+\d+)', structures, re.IGNORECASE)
        return [(re.split(r'\s+', line)[0], re.split(r'\s+', line)[-1]) for line in prostate_data]
    return []

def write_to_csv(log_files, output_csv):
    data_list = []
    for log_file in log_files:
        patient_id = re.search(r'(\d{4})', os.path.basename(log_file)).group(0)
        prostate_data = extract_prostate_data(log_file)
        for struct_name, voxel_count in prostate_data:
            data_list.append((patient_id, struct_name, voxel_count))
    
    # Sort data list by patient ID numerically
    data_list.sort(key=lambda x: int(x[0]))
    
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Patient ID', 'Structure', 'Voxel Count'])
        for row in data_list:
            csvwriter.writerow(row)

# Base path and execution
base_path = '/home/mjm/Documents/UBC/Research/nextgenbrachy/patient data/Prostate Patients (Dakota 2022-2020)'
log_files = find_log_files(base_path)
output_csv = base_path+'/'+'prostate_voxel_counts.csv'
write_to_csv(log_files, output_csv)
