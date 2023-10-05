import subprocess
import pandas as pd
import os
import time
import concurrent.futures
import sys
from dotenv import load_dotenv
from pdf_summary import summary_pdf, merge_df, overall_summary_report
from operations import speed_calc, resolution_check, altitude_check, white_balance_check, getUnix, summary, console_parameters, convert_to_degree, check_angle
from log_it import log

load_dotenv()

def analysis(all_exif_data, csv_filename):
    df = pd.DataFrame(all_exif_data)
    if not df.empty:
        #Removing - sign from values
        pos_df = df['Speed X'].str.replace('-', '')
        #Average of first 1000 images on Speed X parameter
        avg = pos_df[:1000].astype(float).mean()
        #UTC to Unix Time conversion
        df = getUnix(df)
        df['FloatGPSLatitude'] = df.apply(lambda row : convert_to_degree(row['GPS Latitude']), axis = 1)
        df['FloatGPSLongitude'] = df.apply(lambda row : convert_to_degree(row['GPS Longitude']), axis = 1)
        df['Speed'] =             df.apply(lambda row: speed_calc(row['Speed X'], row['Speed Y'], row['Speed Z'], avg)[0], axis=1)
        df['isSpeedWithinLimits'] = df.apply(lambda row: speed_calc(row['Speed X'], row['Speed Y'], row['Speed Z'], avg)[1], axis=1)
        df['isMegaPixelGreaterThan12'] = df.apply(lambda row:resolution_check(row['Megapixels']),axis=1)
        df['isAltitudeWithinLimits'] = df.apply(lambda row:altitude_check(row['Relative Altitude']),axis=1)
        df['Angle'] = df.apply(lambda row: check_angle(row['Gimbal Pitch Degree']), axis = 1)
        df['isWhiteBalanceAuto'] = df.apply(lambda row: white_balance_check(row['White Balance']),axis=1)
        boolean_columns = ['isSpeedWithinLimits', 'isMegaPixelGreaterThan12', 'isAltitudeWithinLimits', 'isWhiteBalanceAuto', 'Angle']
        df['QC Status'] = df[boolean_columns].all(axis=1).apply(lambda x: 'Passed' if x else 'Failed')
       
        
        summary_df = summary(df)
        #Displaying parameter values
        console_parameters(df)        
        #Generate PDF summary statistics
        summary_pdf(df, os.path.dirname(csv_filename))
        merge_df(df)
        # Create a writer to save data to an Excel file
        with pd.ExcelWriter(csv_filename) as writer:
            df.to_excel(writer, sheet_name='AnalysisOfMetadata', index=False)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
    else:
        log("ERR","No metadata found from the directory.")

# Function to save metadata to a CSV file
def save_metadata_to_excel(metadata, csv_filename):   
    if metadata:
        df = pd.DataFrame(metadata)
        df.to_excel(csv_filename, index=False)
        log("INF", f"Metadata saved to {csv_filename}")
    else:
        log("ERR", "No metadata file generated")       
   

def get_exif_data(image_path):
    try:
        result = subprocess.check_output(["exiftool", image_path])
        exif_data = result.decode('utf-8')
        return exif_data.splitlines()
    except Exception as e:
        log("ERR", f"Error from exiftool during metadata extraction: {e}")
        return None
    
def process_image(image_path):
    exif_dict = {}
    exif_data = get_exif_data(image_path)
    if exif_data:
        for line in exif_data:
            tag, value = line.split(":", 1)
            tag = tag.strip()  # Remove leading/trailing spaces
            value = value.strip()  # Remove leading/trailing spaces
            exif_dict[tag] = value
        #Add blur/unblur flag
        #exif_dict["isImageClear"] = operations.blur_detection(image_path)
    return exif_dict


# Function to check if a file is an image (you can expand the list of supported extensions)
def is_image(file_path):
    valid_extensions = ['.jpg', '.jpeg','.JPG']
    file_extension = os.path.splitext(file_path)[1].lower()
    return file_extension in valid_extensions

# Function to process a folder
def process_folder(folder_path):
    all_exif_data = []
    # List all files in the directory
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.JPG'))]
    #Multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_image,os.path.join(folder_path,image_file)) for image_file in image_files]
        for future in concurrent.futures.as_completed(futures):
            exif_dict = future.result()
            if exif_dict:
                all_exif_data.append(exif_dict)
        
    # Create a CSV file for the metadata
    csv_filename = os.path.join(folder_path, 'metadata.xlsx')
    save_metadata_to_excel(all_exif_data, csv_filename)   
    log("INF", f"Extraction metadata from: {folder_path} images")
    csv_filename = os.path.join(folder_path, 'analysis.xlsx')
    analysis(all_exif_data , csv_filename)  
    
# Main function to recursively process folders
def main(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        if dirpath:        
            process_folder(dirpath)
        else:
            log("ERR", "Wrong path passed")

if __name__ == "__main__":     
        if len(sys.argv) != 2:
            log("ERR", "Image Path is not Passed")
            log("INF", "Usage: python3 <script.py> <path to the images>")
            sys.exit(1)
        try:
            root_path = sys.argv[1]
            if root_path :
                start_time = time.time()
                main(root_path)    
                overall_summary_report("Final", start_time)
                end_time =time.time()                
                log("INF", f"Execution time: {end_time - start_time} seconds")
        except (ValueError, IndexError) as e:
            log("ERR", "Please ensure the image path")    
            log("INF", "Usage: python3 <script.py> <path to the images>")