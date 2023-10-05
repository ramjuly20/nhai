import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
from reportlab.lib.units import inch
import time
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from graph import plot_graph
from dump_db import load_data_local_infile, insert_into



def summary_pdf(data, path):
    df = pd.DataFrame(data)
    # Add a serial number column to the DataFrame
    df['Serial Number'] = range(1, len(df) + 1)

     # Calculate the counts of accepted and rejected images
    accepted_df = df[df['QC Status'] == 'Passed']
    rejected_df = df[df['QC Status'] == 'Failed']

    accepted_count = len(accepted_df)
    rejected_count = len(rejected_df)
    total_count = len(df)

    accepted_percentage = (accepted_count / total_count) * 100
    rejected_percentage = (rejected_count / total_count) * 100

    pdf_filename = f'{path}/Summary_Report.pdf'
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    elements = []

    # Define a title for the report
    title = Paragraph("QC-Summary Report", getSampleStyleSheet()["Title"])

    # Create a table to display the summary for accepted images
    accepted_summary_data = [['Serial No.', 'File Name', 'DateTime Creation', 'Speed', 'Height', 'MegaPixels', 'WhiteBalance', 'QC Status']]
    for _, row in accepted_df.iterrows():
        accepted_summary_data.append([row['Serial Number'], row['File Name'], row['Date/Time Original'],  row['isSpeedWithinLimits'], row['isAltitudeWithinLimits'], row['isMegaPixelGreaterThan12'], row['isWhiteBalanceAuto'], row['QC Status']])

     # Add rows for the count of accepted and rejected images
    accepted_summary_data.append(['', '', '', '', '', '', 'AcceptedCount', accepted_count])
    accepted_summary_data.append(['','','','','','','Accepted(%)', round(accepted_percentage, 3)])
    accepted_table = Table(accepted_summary_data, colWidths=[50, 90, 100, 50, 50, 70, 70, 70])
    accepted_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    # Create a table to display the summary for rejected images
    rejected_summary_data = [['Serial No.', 'File Name', 'DateTime Creation', 'Speed', 'Height', 'MegaPixels', 'WhiteBalance', 'QC Status']]
    for _, row in rejected_df.iterrows():
        rejected_summary_data.append([row['Serial Number'], row['File Name'], row['Date/Time Original'],  row['isSpeedWithinLimits'], row['isAltitudeWithinLimits'], row['isMegaPixelGreaterThan12'], row['isWhiteBalanceAuto'], row['QC Status']])
    rejected_summary_data.append(['', '', '', '', '', '', 'RejectedCount', rejected_count])
    rejected_summary_data.append(['','','','','','','Rejected(%)', round(rejected_percentage, 3)])
    rejected_table = Table(rejected_summary_data, colWidths=[50, 90, 100, 50, 50, 70, 70, 70])
    rejected_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    # Add the title to the summary
    elements.append(title)

    # Add the accepted table to the elements list
    elements.append(Paragraph(f"Accepted Images ({accepted_count}/{total_count})", getSampleStyleSheet()["Heading1"]))
    elements.append(accepted_table)

    # Add the rejected table to the elements list
    elements.append(Paragraph(f"Rejected Images ({rejected_count}/{total_count})", getSampleStyleSheet()["Heading1"]))
    elements.append(rejected_table)

    # Build the PDF report
    doc.build(elements)

    print(f"PDF report generated: {pdf_filename}")


merged_df = None
def merge_df(data):
    global merged_df  # Declare merged_df as a global variable

    # If merged_df is None, initialize it with the first dataframe
    if merged_df is None:
        merged_df = data
    else:
        # Merge the incoming dataframe with the accumulated dataframe
        merged_df = pd.concat([merged_df, data], ignore_index=True)
    

def overall_summary_report(pdf_filename, start_time):    
    df = pd.DataFrame(merged_df)
    start = time.time()
    load_data_local_infile(df)
    print("Time taken for execution from load_data_local_infile", (time.time() - start))
    start = time.time()
    insert_into(df)
    print("Time taken for execution from insert_into", (time.time() - start))
    # Calculate the counts of accepted and rejected images
    accepted_df = df[df['QC Status'] == 'Passed']
    rejected_df = df[df['QC Status'] == 'Failed']
    accepted_df['Image Description'] = accepted_df['Directory'] + '/' + accepted_df['File Name']
    rejected_df['Image Description'] = rejected_df['Directory'] + '/' + rejected_df['File Name']

    accepted_df = accepted_df.sort_values(by='Image Description')
    rejected_df = rejected_df.sort_values(by='Image Description')

    accepted_count = len(accepted_df)
    rejected_count = len(rejected_df)
    total_count = len(df)

    accepted_df['Serial Number'] = range(1, accepted_count + 1)
    rejected_df['Serial Number'] = range(1, rejected_count + 1)    


    accepted_percentage = (accepted_count / total_count) * 100
    rejected_percentage = (rejected_count / total_count) * 100

    #Plotting Graph
    plt = plot_graph(accepted_percentage, rejected_percentage)
    pie_chart_image = 'pie_chart.png'
    plt.savefig(pie_chart_image, bbox_inches='tight', pad_inches=0.1)
    plt.close()


    pdf_filename = f'{pdf_filename}.pdf'
    doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter), leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Define custom styles for header and page number
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Header', fontSize=16, alignment=1))

    elements = []

    # Add a Spacer to create space between content elements
    space_height = 0.5 * inch  # Adjust the height as needed
    space = Spacer(1, space_height)
   
    from datetime import datetime, timedelta

    # Get the current UTC time
    utc_time = datetime.utcnow()
    # Calculate the offset for IST (UTC+5:30)
    ist_offset = timedelta(hours=5, minutes=30)
    # Convert UTC time to IST time
    ist_time = utc_time + ist_offset

    # Define a title for the report
    title = Paragraph(f"NHAI QC System Generated Report - KPMG/DronaMaps - {ist_time.strftime('%Y-%m-%d %I:%M %p')}", getSampleStyleSheet()["Title"])
    title_summary = Paragraph("<font size='14'>Summary Table</font>", getSampleStyleSheet()["Title"])
    accept_table = Paragraph("<font size='14'>Passed Images</font>", getSampleStyleSheet()["Title"])
    reject_table = Paragraph("<font size='14'>Failed Images</font>", getSampleStyleSheet()["Title"])
    graph_table = Paragraph("<font size='14'>Image QC Distribution</font>", getSampleStyleSheet()["Title"])

    # Create a table to display the summary for accepted images
    accepted_summary_data = [['S.No.', 'Image Name', 'DateTime Creation', 'Speed', 'Height', 'MegaPixels', 'WhiteBalance', 'QC Status']]
    for _, row in accepted_df.iterrows():
        accepted_summary_data.append([row['Serial Number'], row['Image Description'], row['Date/Time Original'],  round(float(row['Speed']),2), round(float(row['Relative Altitude']), 2), round(float(row['Megapixels']), 2), row['White Balance'], row['QC Status']])

    accepted_table = Table(accepted_summary_data, colWidths=[None, None, None, None, None, None, None, None] ) #colWidths=[50, 120, 100, 50, 50, 70, 70, 70]
    accepted_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    # Create a table to display the summary for rejected images
    rejected_summary_data = [['S.No.', 'Image Name', 'DateTime Creation', 'Speed', 'Height', 'MegaPixels', 'WhiteBalance', 'QC Status', 'Failure Reason']]
    for _, row in rejected_df.iterrows():
        speed = round(float(row['Speed']), 2)
        height = round(float(row['Relative Altitude']), 2)
        megapixel = round(float(row['Megapixels']), 2)
        white_bal = row['White Balance']
        reason = ''
        if speed > float(os.environ['SPEED']) or height > float(os.environ['HEIGHT']) or megapixel < float(os.environ['MEGAPIXEL']):
            if speed > float(os.environ['SPEED']):
                reason += 'Overspeed'
            if height > float(os.environ['HEIGHT']):
                if reason:
                    reason += ', '
                reason += 'Overheight'
            if megapixel < float(os.environ['MEGAPIXEL']) or white_bal != os.environ['WHITE_BALANCE']:
                if reason:
                    reason += ', '
                reason += 'Low-resolution'
        rejected_summary_data.append([row['Serial Number'], row['Image Description'], row['Date/Time Original'],  round(float(row['Speed']), 2), round(float(row['Relative Altitude']),2), round(float(row['Megapixels']),2), row['White Balance'], row['QC Status'], reason if reason else 'N/A'])
    rejected_table = Table(rejected_summary_data, colWidths=[None, None, None, None, None, None, None, None])
    rejected_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    # Add the title to the summary
    elements.append(title)
    elements.append(space)

    # Create a custom ParagraphStyle with your desired font and font size
    custom_style = ParagraphStyle(name='CustomStyle', fontName='Helvetica-Bold', fontSize=11, leading=14 ,  leftIndent=0.5*inch)

    #Add AcceptedCount and Accepted(%) separately
    elements.append(Paragraph(f'Total Images: {accepted_count + rejected_count}', custom_style))
    elements.append(Paragraph(f'Passed: {accepted_count}, ({round(accepted_percentage, 3)}%)', custom_style))
    elements.append(Paragraph(f'Failed: {rejected_count}, ({round(rejected_percentage, 3)}%)', custom_style))
    elements.append(space)
    elements.append(graph_table)
    
    # Load the pie chart image into the PDF using Image class
    image = Image(pie_chart_image, width=4 * inch, height=3 * inch)
    elements.append(image)
    #elements.append(space)
    
    summary_data = [
    ['Speed', df['Speed'].min(), round(float(df['Speed'].max()),3), os.environ['SPEED']],
    ['Altitude', round(float(df['Relative Altitude'].min()), 2), round(float(df['Relative Altitude'].max()), 2), os.environ['HEIGHT']],
    ['MegaPixel', df['Megapixels'].min(), df['Megapixels'].max(), os.environ['MEGAPIXEL']],    
    ]
    summary_df = pd.DataFrame(summary_data, columns=['Parameter', 'MinValue', 'MaxValue', 'Threshold'])
    table_data = [list(summary_df.columns)] + summary_df.values.tolist()
    summary_table = Table(table_data, colWidths=None ) 
    summary_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(title_summary)
    elements.append(summary_table)  
    elements.append(space)
    elements.append(accept_table)  
    elements.append(accepted_table) 
    elements.append(space) 
    elements.append(reject_table)
    elements.append(rejected_table)
    elements.append(space)   
    
   
    end_time = time.time()
    
    exec_time = round(end_time - start_time, 3)
    
    formatted_start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))  # Change the format as needed
    formatted_end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))  # Change the format as needed
    elements.append(Paragraph(f'Execution Start Time: {formatted_start_time}', custom_style))
    elements.append(Paragraph(f'Execution End Time: {formatted_end_time}', custom_style))
    elements.append(Paragraph(f'Total Execution Duration: {exec_time} seconds', custom_style))
    
    doc.build(elements)
    print(f"PDF report generated: {pdf_filename}")
