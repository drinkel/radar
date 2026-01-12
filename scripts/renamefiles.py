import os
import json

# def check_and_read_json():
#     # Define the file name
#     file_name = 'MeasurementInfo.json'
    
#     # Check if the file exists in the current directory
#     if os.path.exists(file_name):
#         print(f"File '{file_name}' found.")
        
#         # Open and load the JSON file
#         with open(file_name, 'r') as file:
#             try:
#                 data = json.load(file)
                
#                 # Look for the "DataFormat" key in the JSON data
#                 if "DataFormat" in data:
#                     print("DataFormat:", data["DataFormat"])
#                 else:
#                     print("'DataFormat' key not found in JSON file.")
#             except json.JSONDecodeError:
#                 print("Error reading JSON file. The file might be malformed.")
#     else:
#         print(f"File '{file_name}' not found.")



def checkMeasurementInfo():
	jsonfile = "measurementInfo.json"
	if os.path.exists(jsonfile):
		print("je tu")
		with open(jsonfile, 'r') as file:
        	data = json.load(file)
        	if "DataFormat" in data:
            	print(data["DataFormat"])
			else:
				print("DataFormat not found in measurementInfo!")


	else:
        print("measurementInfo.json not found!")
        
# def renameFiles():
#     current_directory = os.getcwd()
#     directories = []

#     for item in os.listdir(current_directory):
#         if os.path.isdir(os.path.join(current_directory, item)):
#             directories.append(os.path.join(current_directory, item))


#     for directory in directories:
#         for filename in os.listdir(directory):
#             if filename.endswith(".csv"):
#                 print(filename)
#         #         file_path = os.path.join(directory, filename)
#         #         new_filename = filename[:-4] + "_0.csv"
#         #         new_file_path = os.path.join(directory, new_filename)
#         #         os.rename(file_path, new_file_path)

#         print(f"Renamed files in directory: {directory}")

if __name__ == "__main__":
    checkMeasurementInfo()
    # renameFiles()