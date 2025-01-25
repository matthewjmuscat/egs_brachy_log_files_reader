import os
import re
import csv

def find_log_files(base_path):
    # This function finds all log files within the specified path structure
    patient_folders = [f for f in os.listdir(base_path) if re.match(r'PT\d{4}', f)]
    log_files = []
    for folder in patient_folders:
        folder_path = os.path.join(base_path, folder)  # Full path to the patient folder
        tg43_path = os.path.join(folder_path, 'TG43', 'phantom')

        # Check if the patient folder is a directory
        if not os.path.isdir(folder_path):
            continue  # Skip to the next iteration if not a directory

        # Check if the TG43/phantom directory exists before attempting to access it
        if os.path.exists(tg43_path):
            # Extract the four-digit number from the folder name
            folder_number = re.search(r'PT(\d{4})', folder).group(1)
            
            # Scan for log files containing the same four-digit number
            for file in os.listdir(tg43_path):
                if re.search(folder_number, file) and file.endswith('.log'):
                    log_files.append(os.path.join(tg43_path, file))
        else:
            print(f"Skipping {folder}: TG43/phantom directory does not exist.")
    return log_files

def extract_media_data(log_file_path):
    # Extracts media data for P50C50 and CALCIFICATION_ICRU46 from the given log file
    with open(log_file_path, 'r') as file:
        content = file.read()
    
    # Find media voxel count section and extract specific media counts
    media_pattern = r'Media voxel count:(.*?)(?:---|$)'
    media_match = re.search(media_pattern, content, re.DOTALL)
    p50c50_count = calcification_count = '0'  # Default to 0 if not found
    if media_match:
        media_data = media_match.group(1).strip()
        p50c50_match = re.search(r'P50C50\s+(\d+)', media_data)
        calcification_match = re.search(r'CALCIFICATION_ICRU46\s+(\d+)', media_data)
        if p50c50_match:
            p50c50_count = p50c50_match.group(1)
        if calcification_match:
            calcification_count = calcification_match.group(1)
    return p50c50_count, calcification_count

def write_to_csv(log_files, output_csv):
    # Prepare data list
    data_list = []
    
    # Collect all data
    for log_file in log_files:
        # Extract any four-digit number from the log file name
        match = re.search(r'\d{4}', os.path.basename(log_file))
        if match:
            patient_id = match.group(0)  # .group(0) gets the entire match
            p50c50_count, calcification_count = extract_media_data(log_file)
            data_list.append((patient_id, p50c50_count, calcification_count))
        else:
            print(f"No valid patient ID found in filename {os.path.basename(log_file)}")
    
    # Sort data list by patient ID (first element of each tuple)
    data_list.sort(key=lambda x: int(x[0]))  # Converts string to int for numerical sorting

    # Write sorted data to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Patient ID', 'P50C50', 'CALCIFICATION_ICRU46'])
        for row in data_list:
            csvwriter.writerow(row)




# Base path where the patient data is stored
#base_path = '/home/mjm/Documents/UBC/Research/nextgenbrachy/patient data/Prostate Patients (Dakota 2022-2020)'
base_path = '/home/mjm/Documents/UBC/Research/nextgenbrachy/patient data/Prostate Patients (Matt 2022-2020)'
log_files = find_log_files(base_path)
output_csv = base_path+'/'+'calcification_voxel_counts.csv'  # Define your output CSV file path here
write_to_csv(log_files, output_csv)

print("Finished! Press Enter to continue...")
input()
