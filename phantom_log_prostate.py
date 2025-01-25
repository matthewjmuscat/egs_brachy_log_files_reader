import os
import re
import csv

def find_log_files(base_path):
    # This function finds all log files within the specified path structure
    patient_folders = [f for f in os.listdir(base_path) if re.match(r'PT\d{4}', f)]
    log_files = []
    for folder in patient_folders:
        tg43_path = os.path.join(base_path, folder, 'TG43', 'phantom')
        # Scan for log files matching the patient folder's four-digit code
        for file in os.listdir(tg43_path):
            if re.search(folder, file) and file.endswith('.log'):
                log_files.append(os.path.join(tg43_path, file))
    return log_files

def extract_prostate_data(log_file_path):
    # Extracts prostate structure data from the given log file
    with open(log_file_path, 'r') as file:
        content = file.read()
    
    # Looking for the part of the log with structure voxel counts
    match = re.search(r'Structure voxel count:(.*?)(?:---|$)', content, re.DOTALL)
    if match:
        structures = match.group(1).strip()
        # Find all prostate-related lines
        prostate_data = re.findall(r'(Prostate[\w_]*\s+\d+)', structures)
        return [(re.split(r'\s+', line)[0], re.split(r'\s+', line)[-1]) for line in prostate_data]
    return []

def write_to_csv(log_files, output_csv):
    # Write extracted data to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Log File', 'Structure', 'Voxel Count'])
        for log_file in log_files:
            prostate_data = extract_prostate_data(log_file)
            for struct_name, voxel_count in prostate_data:
                csvwriter.writerow([os.path.basename(log_file), struct_name, voxel_count])

# Base path where the patient data is stored
base_path = '/home/mjm/Documents/UBC/Research/nextgenbrachy/patient data/Prostate Patients (Dakota 2022-2020)'
log_files = find_log_files(base_path)
output_csv = '/path/to/your/output.csv'  # Define your output CSV file path here
write_to_csv(log_files, output_csv)
