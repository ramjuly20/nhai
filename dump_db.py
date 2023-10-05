from db import connection as con
from sqlalchemy import create_engine
from log_it import log
import pandas as pd
import math


import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='ram',
    database='nhai',
    allow_local_infile=True
)  

def load_data_local_infile(dataframe, csv_filename = None):
    df = pd.DataFrame(dataframe)
    df.to_csv('./out.csv', index=False)

    # Use MySQL's LOAD DATA INFILE statement
    sql = """LOAD DATA LOCAL INFILE './out.csv' INTO TABLE meta_analysis
            FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '' LINES TERMINATED BY '\n'
            IGNORE 1 LINES ( `ExifToolVersionNumber` ,`FileName` ,`Directory` ,`FileSize` ,`FileModificationDateTime` ,`FileAccessDateTime` ,`FileInodeChangeDateTime` ,`FilePermissions` ,`FileType` ,`FileTypeExtension` ,`MIMEType` ,`JFIFVersion` ,`ExifByteOrder` ,`ImageDescription` ,`CameraModelName` ,`Orientation` ,`XResolution` ,`YResolution` ,`ResolutionUnit` ,`Software` ,`ModifyDate` ,`YCbCrPositioning` ,`ExposureTime` ,`FNumber` ,`ExposureProgram` ,`ISO` ,`ExifVersion` ,`DateTimeOriginal` ,`CreateDate` ,`ComponentsConfiguration` ,`CompressedBitsPerPixel` ,`ShutterSpeedValue` ,`ApertureValue` ,`ExposureCompensation` ,`MaxApertureValue` ,`SubjectDistance` ,`MeteringMode` ,`LightSource` ,`Flash` ,`FocalLength` ,`Warning` ,`Make` ,`SpeedX` ,`SpeedY` ,`SpeedZ` ,`Pitch` ,`Yaw` ,`Roll` ,`CameraPitch` ,`CameraYaw` ,`CameraRoll` ,`FlashpixVersion` ,`ColorSpace` ,`ExifImageWidth` ,`ExifImageHeight` ,`InteroperabilityIndex` ,`InteroperabilityVersion` ,`ExposureIndex` ,`FileSource` ,`SceneType` ,`CustomRendered` ,`ExposureMode` ,`WhiteBalance` ,`DigitalZoomRatio` ,`FocalLengthIn35mmFormat` ,`SceneCaptureType` ,`GainControl` ,`Contrast` ,`Saturation` ,`Sharpness` ,`SubjectDistanceRange` ,`SerialNumber` ,`GPSVersionID` ,`GPSLatitudeRef` ,`GPSLongitudeRef` ,`GPSAltitudeRef` ,`XPComment` ,`XPKeywords` ,`Compression` ,`ThumbnailOffset` ,`ThumbnailLength` ,`About` ,`Format` ,`AbsoluteAltitude` ,`RelativeAltitude` ,`GimbalRollDegree` ,`GimbalYawDegree` ,`GimbalPitchDegree` ,`FlightRollDegree` ,`FlightYawDegree` ,`FlightPitchDegree` ,`CamReverse` ,`GimbalReverse` ,`SelfData` ,`CalibratedFocalLength` ,`CalibratedOpticalCenterX` ,`CalibratedOpticalCenterY` ,`RtkFlag` ,`Version` ,`HasSettings` ,`HasCrop` ,`AlreadyApplied` ,`ImageWidth` ,`ImageHeight` ,`EncodingProcess` ,`BitsPerSample` ,`ColorComponents` ,`YCbCrSubSampling` ,`Aperture` ,`ImageSize` ,`Megapixels` ,`ScaleFactorTo35mmEquivalent` ,`ShutterSpeed` ,`ThumbnailImage` ,`GPSAltitude` ,`GPSLatitude` ,`GPSLongitude` ,`CircleOfConfusion` ,`FieldOfView` ,`GPSPosition` ,`HyperfocalDistance` ,`LightValue` ,`unix_ModifyDate` ,`unix_DateTimeOriginal` ,`FloatGPSLatitude` ,`FloatGPSLongitude` ,`Speed` ,`isSpeedWithinLimits` ,`isMegaPixelGreaterThan12` ,`isAltitudeWithinLimits` ,`Angle` ,`isWhiteBalanceAuto` ,`QCStatus` ,`MPFVersion` ,`NumberOfImages` ,`MPImageFlags` ,`MPImageFormat` ,`MPImageType` ,`MPImageLength` ,`MPImageStart` ,`DependentImage1EntryNumber` ,`DependentImage2EntryNumber` ,`ImageUIDList` ,`TotalFrames` ,`PreviewImage` )"""

    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()

    # Close the cursor and the database connection
    cursor.close()
    db.close()

def insert_into(dataframe):
    conn = con()
    cursor = conn.cursor()
    df = pd.DataFrame(dataframe)
    colname = []
    for i in range(len(df)):
        row = df.loc[i]
        # Iterate through the row and preparing columns
        for key, value in row.items():
            col = key.split()            
            colname.append("".join(col))
        break

    for index, row in df.iterrows():
        #Removing / from columns
        cols= [word.replace('/', '') for word in colname]
        cols_name = ",".join(cols)
        row_val = tuple(row)
        #Converting nan from dataframe row to NULL for MySQLDB
        cleaned_tuple = tuple("NULL" if isinstance(x, float) and math.isnan(x) else x for x in row_val)
        sql = f"insert into meta_analysis({cols_name}) values {cleaned_tuple}"
        cursor.execute(sql)
        conn.commit()
    
    # Close the cursor and the database connection
    cursor.close()
    db.close()