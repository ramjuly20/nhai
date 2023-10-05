import math
import os
import pandas as pd
from datetime import datetime
from log_it import log


# function for summary - min max and threshold value
def summary(df):
    summary_df = pd.DataFrame(columns=['Tag','Threshold','Min','Max','Buffer', 'Height Status'])
    summary_df['Tag'] = ['SPEED','HEIGHT','MEGAPIXEL','ANGLE',
                         'WHITE_BALANCE','BLUR_THRESHOLD_LAPLACE','BLUR_THRESHOLD_VARIANCE','SIMILARITY', 'Float_GPS_Latitude', 'Float_GPS_Longitude']
    summary_df['Threshold']=[os.environ["SPEED"],os.environ["HEIGHT"],os.environ["MEGAPIXEL"],os.environ["ANGLE"],os.environ["WHITE_BALANCE"]
                         ,os.environ['BLUR_THRESHOLD_LAPLACE'],os.environ['BLUR_THRESHOLD_VARIANCE'],os.environ['SIMILARITY'], 'NA', 'NA']
    summary_df['Min'] = [df['Speed'].abs().min(),df['Relative Altitude'].astype(float).abs().min(),df['Megapixels'].astype(float).abs().min(),'','NA','NA','NA','NA', df['FloatGPSLatitude'].astype(float).abs().min(), df['FloatGPSLongitude'].astype(float).abs().min()]
    summary_df['Max'] = [df['Speed'].abs().max(),df['Relative Altitude'].astype(float).abs().max(),df['Megapixels'].astype(float).abs().max(),'','NA','NA','NA','NA', df['FloatGPSLatitude'].astype(float).abs().max(), df['FloatGPSLongitude'].astype(float).abs().max()]
    summary_df['Buffer'] = [os.environ['BUFFER_SPEED'],os.environ['BUFFER_HEIGHT'],'','','','','','', '', '']
    
    # Update 'Height Status' for the 'HEIGHT' row
    height_min = summary_df.loc[summary_df['Tag'] == 'HEIGHT', 'Min'].values[0]
    height_max = summary_df.loc[summary_df['Tag'] == 'HEIGHT', 'Max'].values[0]
    height_ratio = float(os.environ['HEIGHT_RATIO'])

    if height_max / height_min < height_ratio:
        summary_df.loc[summary_df['Tag'] == 'HEIGHT', 'Height Status'] = 'Pass'
    else:
        summary_df.loc[summary_df['Tag'] == 'HEIGHT', 'Height Status'] = 'Fail'
    return summary_df

# function for unix timestamp
def convert_date_str_to_unix(df, column_name):
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the DataFrame.")
    df[f'unix_{column_name}'] = df[column_name].apply(lambda x: datetime.strptime(x, '%Y:%m:%d %H:%M:%S').timestamp())
    return df

# get UNIX timestamp
def getUnix(exif_dict):
    exif_dict = convert_date_str_to_unix(exif_dict,'Modify Date')
    exif_dict = convert_date_str_to_unix(exif_dict,'Date/Time Original')
    pd.options.display.float_format = '{:.0f}'.format
    return exif_dict

"""#Function for blur detection (More faster in execution)
def blur_detection(image_path):
    threshold = float(os.environ['BLUR_THRESHOLD_LAPLACE'])
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    return False if fm < threshold else True"""

#Speed Calc and Flag
def speed_calc(speedX,speedY,speedZ, avg):
    speedX, speedY, speedZ= float(speedX), float(speedY), float(speedZ)
    buffer_speed, speed_env = float(os.environ["BUFFER_SPEED"]), float(os.environ["SPEED"])
    speed = buffer_speed + speed_env
    #Applying RMS on three parameters like X, Y and Z     
    rms_speed = math.sqrt((speedX**2 + speedY**2 + speedZ**2)/3)
    #Comparing RMS with first 1000 images mean from SpeedX parameter
    #print(f"Average: {avg}, RMS: {rms_speed}", (rms_speed <= avg))
    flag = True if rms_speed <= speed else False
    return rms_speed, flag

#Megapixel Flag
def resolution_check(res):
    threshold = float(os.environ['MEGAPIXEL'])
    flag = False if float(res) < threshold else True
    return flag

#Altitude Flag
def altitude_check(alt):
    threshold = float(os.environ['HEIGHT']) + float(os.environ['BUFFER_HEIGHT'])
    flag = True if float(alt) <= threshold else False  #Should be 40
    return flag

#WhiteBalance Flag
def white_balance_check(wb):
    threshold = os.environ["WHITE_BALANCE"]
    flag = True if wb == threshold else False
    return flag

#Type Flag
def type_check(type):
    threshold = os.environ['TYPE']
    flag = True if type == threshold else False
    return flag

def console_parameters(df):
    for index in range(len(df)):
        row = df.iloc[index]
        log("INF", f"FileName: {row['File Name']} - FileCreationDatetime: {row['Date/Time Original']} - UnixTimeStamp : {row['unix_Date/Time Original']} - (MegaPixel: {row['Megapixels']}, Threshold: {os.environ['MEGAPIXEL']}) - (Speed: {row['Speed']},Threshold: {float(os.environ['SPEED']) + float(os.environ['BUFFER_SPEED'])}) - (Height: {(row['Relative Altitude'])},Threshold: {float(os.environ['HEIGHT']) + float(os.environ['BUFFER_HEIGHT'])}) - (WhiteBalance: {row['White Balance']},Threshold: {os.environ['WHITE_BALANCE']}) - (GimbalPitchAngle: {abs(float(row['Gimbal Pitch Degree']))},Threshold: {os.environ['ANGLE']}) - QC-Status: {row['QC Status']}")
    

def convert_to_degree(row):    
    parts = row.split()
    degrees = parts[0]
    minutes = parts[2].replace("'", '')
    seconds = parts[3].replace('"', '')
    direction = parts[4]
    decimal_degrees = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if direction == 'E' or direction == 'N':
        decimal_degrees = -decimal_degrees
    return abs(decimal_degrees)


def check_angle(row):
    min_angle_env = float(os.environ['MIN_ANGLE'])
    max_angle_env = float(os.environ['MAX_ANGLE'])    
    angle_cal = abs(float(row))
    flag = True if angle_cal >= min_angle_env or angle_cal <= max_angle_env else False
    return flag 