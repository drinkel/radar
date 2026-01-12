import os
import json
import glob 

class fileManagement:
	def __init__(self):
		self.needToRenameFiles = False
		self.wrongFileName = True 

		self.checkMeasurementInfo()
		if (self.needToRenameFiles):
			self.checkCorrectFilenames()
			if (self.wrongFileName):
				self.renameFiles()
				self.addFakeDataFormat()
				self.addFakeToOpts()




	def checkMeasurementInfo(self):
		### check json file if you need to edit file names
		### 3 parameters (node_CF_UnCF = no need for renaming)
		### 2 parameters (node_CF = renaming is necessary)
		jsonfile = os.getcwd()
		jsonfile += "/measurementInfo.json"
		lines = []
		if os.path.exists(jsonfile):
			with open(jsonfile, 'r') as file:
				for line in file:
					lines.append(line.strip())
			file.close()

			for line in lines:
				if "DataFormat" in line:
					splitted = line.split("_")
					if (len(splitted) == 3):
						print("No need to rename csv files")
					elif (len(splitted) == 2):
						self.firstelement = splitted[0].split(":")
						self.firstelement = self.firstelement[1]
						self.firstelement = self.firstelement.split("\"")
						self.firstelement = self.firstelement[1]
						splitted[1] = splitted[1][:-2]
						self.secondelement = splitted[1]
						self.needToRenameFiles = True
					else: 
						print("Error in measurementInfo.json, DataFormat line")
					
		else:
			print("measurementInfo.json not found!")


	def checkCorrectFilenames(self):
		### check if all files have only one parameter in their names
		rootpath = os.getcwd()
		directories = []
		for item in os.listdir(rootpath):
			if os.path.isdir(os.path.join(rootpath, item)):
				directories.append(os.path.join(rootpath, item))

		for directory in directories:
			for root, dirs, files in os.walk(directory):
				for name in files:
					splittednames = name.split("_")
					if (len(splittednames) == 3):
						self.wrongFileName = False

		if not self.wrongFileName:
			### if all files dont have correct name format, no changing of filenames
			print("Not all files have wrong filename!")



	def renameFiles(self):
		rootpath = os.getcwd()
		directories = []

		for item in os.listdir(rootpath):
			if os.path.isdir(os.path.join(rootpath, item)):
				directories.append(os.path.join(rootpath, item))

		counter = 0
		for directory in directories:
			for filename in os.listdir(directory):
				if filename.endswith(".csv"):
					counter += 1
					file_path = os.path.join(directory, filename)
					new_filename = filename[:-4] + "_0.csv"
					new_file_path = os.path.join(directory, new_filename)
					os.rename(file_path, new_file_path)


			# print(f"Renamed files in directory: {directory}")
		print("Totally renamed ", counter, " files")

	def addFakeDataFormat(self):
		jsonfile = os.getcwd()
		jsonfile += "/measurementInfo.json"
		lines = []

		if os.path.exists(jsonfile):
			with open(jsonfile, 'r') as file:
				data = json.load(file)
			keys = data.keys()
			items = list(data.items())
			prev_format = data["DataFormat"]
			prev_format += "_fake"
			data["DataFormat"] = prev_format
			out_file = open(jsonfile, "w")
			json.dump(data, out_file, indent=4)
			print("Updated measurementInfo.json")
		else:
			print("measurementInfo.json not found!")
	
	def addFakeToOpts(self):
		root = os.getcwd()

		optsfiles = glob.glob(os.path.join(root, '*.opts'))
		if (len(optsfiles) == 1):
			with open(optsfiles[0], 'r') as file:
				data = json.load(file)

			def process_dict(d):
				for key, value in list(d.items()):
					if isinstance(value, dict):
						process_dict(value)
					else:
						d[key] = str(value) + ";" if isinstance(value, str) else value
						d["FAKE"] = 0
			process_dict(data)


			json_str = json.dumps(data, indent=4)
			json_str = json_str.replace("},", "}\n,")

			with open(optsfiles[0], 'w') as file:
				file.write(json_str)
			print("Updated *.opts file")




		elif (len(optsfiles) == 0):
			print("No *.opts files!")
		else:
			print("More *.opts files! In root folder should be only one!")

if __name__ == "__main__":
	management = fileManagement()
