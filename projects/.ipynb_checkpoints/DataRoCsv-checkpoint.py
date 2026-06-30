# this code automatically creates a python script in your directory

import pandas as pd
import os

def write_data_to_csv(data, filename):
    """
    Saves a list of dictionaries to a CSV file. 
    Appends seamlessly if the file exists; creates a new one with headers if it doesn't.
    """
    
    # convert the passed data into a DataFrame
    dataframe = pd.DataFrame(data)
        
    # Check if the file already exists on your system using os.path.exists
    file_exists = os.path.exists(filename)
        
    if file_exists:
        # Append data: 'a' mode, turn off headers so columns aren't duplicated in mid-file
        dataframe.to_csv(filename, mode = 'a', header = False, index = False)
        print(f'file {filename} has been successfully updated!')

        
    else:
        # Create new file: 'w' mode (default), write the header columns
        dataframe.to_csv(filename, mode = 'w', header = True, index = False)
        print(f'file {filename} has been successfully created!')