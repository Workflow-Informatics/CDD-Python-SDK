'''
______________________________________________________________________________________________________________________________________________
Copyright © 2022 Workflow Informatics - Distribution of this software without written permission of Workflow Informatics is prohibited.

This SOFTWARE PRODUCT is provided by Workflow Informatics "as is" and "with all faults." 

Workflow Informatics makes no representations or warranties of any kind concerning the safety, suitability, inaccuracies, typographical errors, or other harmful components of this SOFTWARE PRODUCT. 

You are solely responsible for determining whether this SOFTWARE PRODUCT is compatible with your equipment and other software installed on your equipment.

You are solely responsible for the protection of your equipment and backup of your data.

Workflow Informatics will not be liable for any damages you may suffer in connection with using or modifying this SOFTWARE PRODUCT
______________________________________________________________________________________________________________________________________________

This python library encompasses most of the API function calls provided by CDD Vault.

If you're stuck, check out the Quickstart Guide.

'''


import datetime as dt
import pandas as pd

import json
import os
import base64
import re
import requests
import sys
import time
import zipfile

from io import StringIO

helpDir = os.path.join(
				os.path.dirname(__file__),
				"help_docs")


def appendToDocString(*args, **kwargs):
	"""
	:Description: decorates each class method's doc string with
				  descriptions of valid keyword arguments which
				  will in turn be passed to CDD Vault.

				  Mainly used with class methods which implement
				  HTTP verbs (GET, POST, etc.) described in the
				  CDD Vault API.
	"""

	helpDoc = kwargs.get("helpDoc")
	helpDoc = os.path.join(helpDir, helpDoc)
	helpDoc = "\t\t".join(open(helpDoc).readlines())

	if not helpDoc.endswith("\n"): helpDoc += "\n"

	def inner(func):

		func.__doc__ += "\n\n\t\t:Valid CDD Keyword Arguments:\n"
		func.__doc__ += helpDoc

		return func

	return inner


class VaultClient(object):

	def __init__(self, vaultNum, apiKey):

		self.setVaultNumAndURL(vaultNum)
		self.setAPIKey(apiKey)

		self.setMaxSyncObjects()


	def __str__(self):

		return f'Client for Vault ID: {self.vaultNum} instantiated {str(dt.datetime.now())}'


	def setVaultNumAndURL(self, vaultNum):
		"""
		:Description: sets the vault ID and constructs the base URL, from which endpoints
					  for all subsequent API calls (GET, POST, PUT, DELETE) will be constructed.

		:vaultNum (int or str): unique integer ID of the target vault.

		:return (tuple): a two-element tuple consisting of the vault ID and the base URL for
						 accessing the CDD Vault API.
		"""

		self.vaultNum = int(vaultNum)

		URL = "https://app.collaborativedrug.com/api/v1/vaults/"
		URL = URL + str(vaultNum)

		self.URL = URL

		return (self.vaultNum, self.URL)


	def getVaultNum(self):
		"""
		:Description: returns the unique integer ID of the target vault.

		:return (int): 
		"""

		return self.vaultNum
	

	def getURL(self):
		"""
		:Description: returns the base URL used in the construction of
					  CDD Vault API calls (GET, POST, PUT, DELETE).

		:return (str):
		"""

		return self.URL


	def setAPIKey(self, apiKey):
		"""
		:Description: sets the API token credentials, which will be passed
					  in the request header to CDD Vault with each API request. 

					  Note that the API token must have read/write access to
					  the vault specified by the vault ID when executing the
					  various API calls or an error will be returned.

		:return (str):
		"""

		self.apiKey = apiKey

		return self.apiKey


	def getAPIKey(self):
		"""
		:Description: returns the currently set API key.

		:return (str):
		"""

		return self.apiKey


	def setMaxSyncObjects(self, value=1000):
		"""
		:Description: sets the 'maxSyncObjects' attribute, which is used to determine
					  when a synchronous vs asynchronous export request is submitted
					  to CDD. If the # of objects returned from a GET request is ever
					  >= maxSyncObjects, the call will be repeated asynchronously.

					  Defaults to 1000, the maximum # of objects which a CDD GET request
					  can return synchronously.

					  Only used in methods where GET requests can be performed asynchronously:
					  Molecules, Batches, Plates, Protocols, and Protocol Data. See method
					  sendSyncAndAsyncGets().
		"""

		self.maxSyncObjects = value

		return self.maxSyncObjects


	def getValidKwargs(self, fileName):
		"""
		:Description: retrieves a list of valid keyword arguments for a 
					  specific CDD Vault API method from the method's 
					  help documentation.
					  
		Valid keywords in help documentation files are identified by:

			1) No white space characters at the start of the line.

			2) A final colon ":" character, after stripping all white space 
			from the end of the line.


		:fileName (str): the name of a valid file containing help documentation for
						 a CDD Vault API method.

		: return (list of str):
		"""

		filePath = os.path.join(helpDir, fileName)

		doc = open(filePath).readlines()

		# Parse help file + locate valid keyword arguments:

		valid_kwargs = [line.rstrip() for line in doc]
		valid_kwargs = [line for line in valid_kwargs if not re.match(r'\s', line)]
		valid_kwargs = [line[:-1] for line in valid_kwargs if line.endswith(":")]

		return valid_kwargs


	def buildQueryString(self, kwargs, valid_kwargs):
		"""
		:Description: Constructs the query string, which will be appended
					  to the URL endpoint when making GET requests.

		:return (str):
		"""

		if len(kwargs) == 0: # No additional query parameters.
			
			return "" 


		# Remove any invalid dictionary keys/parameters from kwargs + warn user, before constructing 
		# the query string:

		for k in list(kwargs):

			if k not in valid_kwargs: 
				
				del kwargs[k]
				print(f"'{k}' is not a valid query parameter.")

			else: kwargs[k] = str(kwargs[k]) # Ensure querys string only contains valid strings.


		# Construct + return the query string:

		queryString = [f"{k}={v}" for k,v in kwargs.items()]
		queryString = "?" + "&".join(queryString)

		return queryString


	def sendGetRequest(self, URL, asText=False, asBytes=False):

		headers = {"X-CDD-Token": self.apiKey}

		response = requests.get(URL, headers=headers)

		response.raise_for_status()

		if asText: return response.text

		elif asBytes: return response.content

		return response.json()


	def sendSyncAndAsyncGets(self, suffix, kwargs, valid_kwargs):
		"""
		:Description: for methods where GET requests can be performed
					  both synchronously and asynchronously, data will
					  first be retrieved using a syncronous GET request.

					  If the # of objects returned is >= 'maxSyncObjects'
					  attribute, the request will be repeated asynchronously
					  to avoid any loss of data.
		"""

		kwargs["page_size"] = self.maxSyncObjects
		queryString = self.buildQueryString(kwargs, valid_kwargs)

		URL = self.URL + suffix + queryString

		objects = self.sendGetRequest(URL)

		if "count" in objects and objects["count"] >= (self.maxSyncObjects - 1):

			kwargs["async"] = "true"
			queryString = self.buildQueryString(kwargs, valid_kwargs)
			URL = self.URL + suffix + queryString

			exportID =self.sendGetRequest(URL)["id"]
			objects = self.getAsyncExport(exportID)

			if type(objects) == dict and objects["status"] == "canceled": 
				
				sys.exit(1)

		else: objects = objects["objects"]

		return objects


	@appendToDocString(helpDoc="get_api_execution_metrics.txt")
	def getAPIExecutionMetrics(self, **kwargs):
		"""
		:Description: return the api usage (both async and sync) in seconds between a particular timeframe. 
					  Use 'after' and 'before' parameters to specify a date range. By default, the time usage 
					  of the previous 30 days are returned. The time returned is for the current API key only.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/13781890848660-Api-Execution-Metrics-GET-
		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_api_execution_metrics.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Send request:

		queryString = self.buildQueryString(kwargs, valid_kwargs)

		suffix = "/api_executions"
		URL = self.URL + suffix + queryString

		usageMetrics = self.sendGetRequest(URL)

		return usageMetrics


	def getAsyncExport(self, exportID, interval=5.0, asText=False, asBytes=False, statusUpdates=True):
		"""
		:Description: used to both check the status of an in-progress CDD asynchronous export,
					  as well as retrieve the data once the export has been completed.

					  Example output: 
					  
					  {'id': 19211628, 'created_at': '2022-11-03T02:02:12.000Z', 
										'modified_at': '2022-11-03T02:02:12.000Z', 'status': 'started'}

		:asText: determines whether the data in response is returned as a json (default behavior) or a string.

		:asBytes: determines whether the data in response is returned as bytes.

		:statusUpdates (bool): if true, displays status updates of asynchronous export to screen.

		:return: json output.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685506-Async-Export-GET-
		"""

		try:
			suffix = f"/export_progress/{exportID}"
			URL = self.URL + suffix

			nonErrorStates = ["new", "started", "finished"] 
			# ^Any export status except these 3 should return an error.

			while True:

				response = self.sendGetRequest(URL)
				if statusUpdates: print(response)
				status = response["status"]

				assert status in nonErrorStates, f"Export status '{status}' indicates the export has failed to complete."

				if status == "finished": break

				time.sleep(interval) # CDD-recommended time-interval for export checks is 5-10 sec.

		except KeyboardInterrupt as e: # Cancels in-progress asynchronous export.

			delResponse = self.deleteExport(exportID)
			if statusUpdates: print(delResponse)

			return delResponse

		
		# Get export data:
		
		suffix = f"/exports/{exportID}"
		URL = self.URL + suffix

		if asText:

			response = self.sendGetRequest(URL, asText=asText)
			return response

		elif asBytes:

			response = self.sendGetRequest(URL, asBytes=asBytes)
			return response

		response = self.sendGetRequest(URL)["objects"]
		return response


	def getBatchMoveJobs(self, batchMoveJobID=None):
		"""
		:Description: retrieve the statuses of one or more batch move jobs from CDD Vault queue.
					  Batch move jobs are used to move a batch to a different molecule in the same vault.
					
					  Note that this request can only be executed by Vault administrators. 

		:batchMoveJobID (int or str): the unique ID of the batch move job to retrieve.
		"""

		suffix = "/batch_move_jobs"
		if batchMoveJobID: 
			suffix += f"/{batchMoveJobID}"

		URL = self.URL + suffix

		batchMoveJobs = self.sendGetRequest(URL=URL)

		return batchMoveJobs


	@appendToDocString(helpDoc="get_batches.txt")
	def getBatches(self, asDataFrame=True, **kwargs):
		"""
		:Description: return a collection of batches from CDD vault. 
		
		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-
		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_batches.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Get batches + format output:

		suffix = "/batches"

		batches = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

		if asDataFrame: batches = pd.DataFrame.from_dict(batches)

		return batches


	@appendToDocString(helpDoc="get_collections.txt")
	def getCollections(self, asDataFrame=True, **kwargs):
		"""
		:Description: return info on collection objects (includes both user and vault collections, by default).

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/18707906579604-Collection-s-GET-POST-PUT-DELETE-
		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_collections.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Get collections + format output:

		suffix = "/collections"

		collections = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

		if asDataFrame: collections = pd.DataFrame.from_dict(collections)

		return collections


	def getDatasets(self, asDataFrame=True):
		"""
		:Description: returns a list of accessible public data sets for the given vault.

		:return: either a json list or a Pandas DataFrame.

		:reference: https://support.collaborativedrug.com/hc/en-us/articles/115005693443-Data-Sets-GET-
		"""

		suffix = "/data_sets"
		URL = self.URL + suffix

		datasets = self.sendGetRequest(URL=URL)
		if asDataFrame: datasets = pd.DataFrame(datasets)
			
		return datasets


	@appendToDocString(helpDoc="get_ELN_entries.txt")
	def getELNEntries(self, asDataFrame=True, 
					  exportPath=None, unzipELNEntries=False, **kwargs):
		"""
		:Description: return information on the ELN entries for the specified vault.

					  Note that this method can only be executed by Vault administrators. 

		:asDataFrame (bool): returns the summary as a Pandas DataFrame. Only used if exportPath=None.

		:exportPath (str): file path for writing zipped ELN entries. Only used if 'exportPath' is not None.
		
						   Note that setting an export path will automatically convert the request to an
						   asynchronous call, which will write a zip file of all available ELN entries to the
						   specified path.

						   If exportPath is None (the default), a summary of the specified ELN entries will instead
						   be returned as a Pandas DataFrame (if asDataFrame=True) or a list of dictionaries.

		:unzipELNEntries (bool): if true, also extracts the zip contents to the 'exportPath' directory.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/360047137852-ELN-Entries-GET-POST-
		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_ELN_entries.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Retrieve summary ELN data:

		if exportPath is None:

			suffix = "/eln/entries" + self.buildQueryString(kwargs, valid_kwargs)
			URL = self.URL + suffix

			elnEntries = self.sendGetRequest(URL)["objects"]
			if asDataFrame: elnEntries = pd.DataFrame(elnEntries)

			return elnEntries


		# Retrieve zipped copy of ELN entries + optional extraction:

		suffix = "/eln/entries?async=true&" + self.buildQueryString(kwargs, valid_kwargs)[1:]
		URL = self.URL + suffix

		exportID = self.sendGetRequest(URL=URL)["id"]
		elnEntries = self.getAsyncExport(exportID=exportID, asBytes=True)

		with open(exportPath, "wb") as f: f.write(elnEntries)

		if unzipELNEntries:

			directory = os.path.splitext(exportPath)[0]
			with zipfile.ZipFile(exportPath, "r") as z:

				z.extractall(directory)


	def getFields(self, asDataFrame=True):
		"""
		:Description: return a list of available fields for the specified vault.

					  This API call will provide you with the “type” and “name” values of *all* fields within a Vault. 
					  The json keys returned by this API call are organized into the following:

					  internal, batch, molecule, protocol

		:return: either a json dict or a dict where each value is a Pandas DataFrame.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/6392675849876-Fields-GET-
		"""

		suffix = "/fields"
		URL = self.URL + suffix

		fields = self.sendGetRequest(URL)
		if asDataFrame: 
			
			fields = {k:pd.DataFrame.from_dict(fields[k]) for k in fields}

		return fields


	def getFile(self, fileID, destFolder=None):
		"""
		:Description: retrieve a single file object from CDD Vault using its file ID.

		:destFolder (str): destination folder where file contents should be written to.
						   File name will default to the original name of the file when
						   it was uploaded to CDD Vault.
		"""

		suffix = f"/files/{fileID}"
		URL = self.URL + suffix

		response = self.sendGetRequest(URL)

		contents = response["contents"]
		contents = base64.b64decode(contents) # Decodes base64-encoded file contents.

		if destFolder:

			fName = response["name"]
			destPath = os.path.join(destFolder, fName)

			with open(destPath, "wb") as f: f.write(contents)

		return contents


	@appendToDocString(helpDoc="get_sample_inventory.txt")
	def getInventorySamples(self, asDataFrame=True, **kwargs):
		"""
		:Description: return sample inventory information for batches in CDD.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/20703796893332-Inventory-Samples-GET-POST-PUT-
		"""

		helpDoc = "get_sample_inventory.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Send request to CDD API:

		suffix = "/inventory_samples"

		samples = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

		if asDataFrame: samples = pd.DataFrame.from_dict(samples)

		return samples


	def getInventoryLocations(self, asDataFrame=True):
		"""
		:Description: Return a list of Sample Inventory Locations for the given Vault

		:return: either a json list or a Pandas DataFrame.

		:reference: https://support.collaborativedrug.com/hc/en-us/articles/21003867672212-Inventory-Locations-GET
		"""

		suffix = "/inventory_locations"
		URL = self.URL + suffix

		locations = self.sendGetRequest(URL=URL)
		if asDataFrame: locations = pd.DataFrame(locations)
			
		return locations

	def getMappingTemplates(self, id=None, asDataFrame=True):
		"""
		:Description: return summary information on all available mapping templates in the specified Vault.

					  Alternatively, if 'id' argument is set, only retrieve details on the data objects mapped 
					  for a specific mapping template.

					  Additional fields when id argument is set include:

						A 'header_mappings' section that identifies the field/readout each header is mapped to.

						A 'file' section that provides details on the original file used to create the template.


		:asDataFrame: returns the json as a Pandas DataFrame. This prm is ignored, if an id value has been set.

		:return: either a json dict or a Pandas DataFrame.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/4413839788436-Mapping-Templates-GET-
		"""

		if id is None:

			suffix = "/mapping_templates"
			URL = self.URL + suffix

			response = self.sendGetRequest(URL)
			if asDataFrame: response = pd.DataFrame.from_dict(response)

		else:

			suffix = f"/mapping_templates/{id}"
			URL = self.URL + suffix

			response = self.sendGetRequest(URL)

		return response


	def getMoleculeImage(self, molID, filePath=None):
		"""
		:Description: retrieve an image of the registered Molecule from CDD identified 
					  by its unique molecule ID.

		modID (int or str): unique ID identifying the molecule for which the image will
							be retrieved.

		:return (bytes): a bytes-object representing the exported molecule image file.
		"""

		suffix = f"/molecules/{molID}/image"

		URL = self.URL + suffix

		exportID = self.sendGetRequest(URL=URL)["id"]

		molImage = self.getAsyncExport(exportID=exportID, asBytes=True)

		if filePath: 

			with open(filePath, "wb") as f: f.write(molImage)

		return molImage


	@appendToDocString(helpDoc="get_molecules.txt")
	def getMolecules(self, asDataFrame=True, **kwargs):
		"""
		:Description: return a list of molecules and their batches, based on optional parameters.
		
		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-
		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_molecules.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Send request to CDD API:

		suffix = "/molecules"

		molecules = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

		if asDataFrame: molecules = pd.DataFrame.from_dict(molecules)

		return molecules


	@appendToDocString(helpDoc="get_plates.txt")
	def getPlates(self, asDataFrame=True, **kwargs):
		"""
		:Description: return a collection of plates from CDD Vault. 
		
		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005739586-Plate-s-GET-DELETE-
		"""
						
		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_plates.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Get plates + format output:

		suffix = "/plates"

		plates = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

		if asDataFrame: plates = pd.DataFrame.from_dict(plates)

		return plates


	def getPlot(self, batchID, protocolID, size="small", destFolder=None):
		"""
		:Description: retrieve dose-response curves/plots for a single Batch.


		"""

		assert size in ["small", "medium", "large"], "Not a valid value."

		suffix = f"/batches/{batchID}/protocols/{protocolID}/plot"

		URL = self.URL + suffix + f"?{size}"; print(URL)

		response = self.sendGetRequest(URL=URL)
		print(response)


	@appendToDocString(helpDoc="get_protocols.txt")
	def getProtocols(self, asDataFrame=True, **kwargs):
		"""
		:Description: return a list of protocols from CDD Vault.
		
		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685406-Protocol-s-GET-
		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_protocols.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Send request to CDD API:

		suffix = f"/protocols"

		protocols = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

		if asDataFrame: protocols = pd.DataFrame.from_dict(protocols)

		return protocols


	@appendToDocString(helpDoc="get_protocol_data.txt")
	def getProtocolData(self, id=None, asDataFrame=True, statusUpdates=True, **kwargs):
		"""
		:Description: returns (a subset of) the readout data for a single protocol using its protocol ID.
					  'id' argument is required, unless 'help' is set to True.
		
		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685426-Protocol-Data-GET-
		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_protocol_data.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Get protocol data + format output:

		suffix = f"/protocols/{id}/data" 

		if "format" in kwargs: # Special behavior for when 'format' arg is included.

			kwargs = {k:v for k,v in kwargs.items() if k in ["format", "runs"]}
			queryString = self.buildQueryString(kwargs, valid_kwargs)

			URL = self.URL + suffix + queryString

			exportID = self.sendGetRequest(URL)["id"]
			data = self.getAsyncExport(exportID, statusUpdates=statusUpdates, asText=True)

			return data


		data = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

		if asDataFrame: data = pd.DataFrame.from_dict(data)

		return data


	def getProjects(self, asDataFrame=True):
		"""
		:Description: returns a list of accessible projects for the given vault.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005693423-Projects-GET-
		"""

		suffix = "/projects"
		URL = self.URL + suffix

		projects = self.sendGetRequest(URL)
		if asDataFrame: projects = pd.DataFrame.from_dict(projects)

		return projects


	@appendToDocString(helpDoc="get_readout_rows.txt")
	def getReadoutRows(self, asDataFrame=True, **kwargs):
		"""
		:Description: return (a subset of) the readout data for any number of protocols.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/360059600831-Readout-Rows-GET-PUT-DELETE-
		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_readout_rows.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Send request to CDD:

		suffix = f"/readout_rows"

		readoutRows = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)
		if asDataFrame: readoutRows = pd.DataFrame(readoutRows)

		return readoutRows


	@appendToDocString(helpDoc="get_runs.txt")
	def getRun(self, runID=None, **kwargs):
		"""
		:Description: retrieve a single run using its unique run ID or a
					  set of runs using their Slurps Import ID, creation dates, etc.

					  Note that kwarg arguments will only be
					  used if 'runID' is set to None (the default).
		
		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/360024315171-Run-s-GET-PUT-DELETE- 
		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_runs.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Send request for single-run to CDD:

		if runID is not None:

			suffix = f"/runs/{runID}"
			URL = self.URL + suffix

			run = self.sendGetRequest(URL)

			return run


		# Send request for multiple runs to CDD:

		queryString = self.buildQueryString(kwargs, valid_kwargs)
		suffix = f"/runs"
		URL = self.URL + suffix + queryString

		runSet = self.sendGetRequest(URL)

		return runSet


	@appendToDocString(helpDoc="get_saved_searches.txt")
	def getSavedSearches(self, searchID=None, format="csv", zip=False, filePath=None, 
										asDataFrame=True, **kwargs):
		"""
		:Description: return either a list of available saved searches if 'searchID' is None
					  or execute a saved search using the specified 'searchID'.

		:searchID (int or str): unique ID for the target saved search. If no search ID
								is provided, will return a list of available saved searches
								along with their corresponding ID's.

		:format (str): valid values are: 'csv', 'xlsx', or 'sdf'. 

					   If format is csv or xlsx, contents will be returned as a DataFrame if 'zip=False'.

					   If format is sdf or 'zip=True', contents will be written to a file instead.

					   'filePath' argument must be set whenever writing to file.
		
		:zip (bool): if True, saved search results will be return as a zip file.

		:filePath (str): a file path where the results from the saved search should be written to.
						 Must be provided if 'zip=True' or 'format=sdf'.

		:asDataFrame (bool): whether to return the search results as a Pandas DataFrame.
							 This is only used if 'searchID=None' (the default).

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005699026-Saved-Search-es-GET-
		"""
		
		def getData():

			# Retrieve the saved search data using an async export.
			# Return as bytes object, regardless of request format.

			suffix = f"/searches/{searchID}"

			# Update query string with format + zip prm values:

			localZip = {True: "true", False: "false"}.get(zip)

			kwargs.update({"format": format, "zip": localZip})

			queryString = self.buildQueryString(kwargs, valid_kwargs)

			# Send request to CDD API:

			URL = self.URL + suffix + queryString

			exportID = self.sendGetRequest(URL)["id"]

			data = self.getAsyncExport(exportID, asBytes=True)

			return data


		def writeToFile(data):

			# Writes the bytes for saved search data to file.

			assert filePath is not None, "Must specify a destination path."

			with open(filePath, "wb") as f: f.write(data)


		def parseBytes(rawData):

			# Read bytes into a Pandas DataFrame, for xlsx or csv data.

			if format == "csv": 
				
				parsedData = StringIO(rawData.decode("utf-8"))
				parsedData = pd.read_csv(parsedData)

			else: parsedData = pd.read_excel(rawData)

			return parsedData


		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_saved_searches.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Retrieve list of available saved searches, if no search ID is provided:

		suffix = f"/searches"

		if searchID is None:

			URL = self.URL + suffix

			savedSearches = self.sendGetRequest(URL)

			if asDataFrame: savedSearches = pd.DataFrame(savedSearches)

			return savedSearches


		# Perform saved search using the specified ID + retrieve search results:

		rawData = getData()

		if filePath or zip or format == "sdf": 
			
			writeToFile(rawData)
			return

		savedSearches = parseBytes(rawData)
		
		return savedSearches


	@appendToDocString(helpDoc="get_users.txt")
	def getUsers(self, **kwargs):
		"""
		:Description: return a list of CDD Vault members. 

					  This method is helpful for identifying user
					  ID's for use with the getELNEntries() method.
		
					  Note that this request can only be executed 
					  by Vault administrators. 

		"""

		# Retrieve valid keyword arguments from help documentation:

		helpDoc = "get_users.txt"
		valid_kwargs = self.getValidKwargs(helpDoc)


		# Send request:

		queryString = self.buildQueryString(kwargs, valid_kwargs)

		suffix = "/users"
		URL = self.URL + suffix + queryString

		users = self.sendGetRequest(URL)

		return users


	@staticmethod
	def getVaults(apiKey, asDataFrame=True):
		"""
		:Description: static method for retrieving a list of Vault instances accesssible to the input API key.

		:return (json object or Pandas DataFrame): 
		"""

		URL = "https://app.collaborativedrug.com/api/v1/vaults"

		headers = {"X-CDD-TOKEN": apiKey}

		response = requests.get(URL, headers=headers)

		response.raise_for_status()
				
		vaults = response.json()

		if asDataFrame: vaults = pd.DataFrame(vaults)

		return vaults


	def sendPostRequest(self, URL, jsonObj):
		"""
		:Description: general method for sending POST requests to CDD vault.

					  'jsonObj' must either be a valid json object, or a string
					  file path pointing to a valid json file.

		"""

		if isinstance(jsonObj, str):
			
			jsonObj = json.load(open(jsonObj, "r"))

		
		headers = {"X-CDD-Token": self.apiKey}

		response = requests.post(URL, headers=headers, json=jsonObj)

		response.raise_for_status()
		
		return response.json()


	@appendToDocString(helpDoc="post_batch_move_job.txt")
	def postBatchMoveJob(self, data=None):
		"""
		:Description: creates a new batch move job to move a batch to a different molecule in the same vault.
		"""

		# Construct URL:

		suffix = "/batch_move_jobs"
		URL = self.URL + suffix


		# Post batch move job to CDD Vault + get response:

		response = self.sendPostRequest(URL, data)

		return response


	@appendToDocString(helpDoc="post_batches.txt")
	def postBatches(self, data=None):
		"""
		:Description: creates a new batch in CDD Vault.

		:data: required, unless 'help' is set to True. Must be either a valid json object,
			   or a string file path to a valid json file.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-
		"""

		# Construct URL:
	
		suffix = "/batches"
		URL = self.URL + suffix
		

		# Post batch to CDD Vault + get response:

		response = self.sendPostRequest(URL, data)

		return response


	def postELNEntries(self, project, title=None, eln_fields={}):
		"""
		:Description: create a new ELN entry in CDD Vault.

		:project (str): the project ID or name where the new ELN entry will be created.

		:title (str): the title of the new ELN entry.

		:eln_fields (dict): a set of configured ELN field/value pairs which have been set by
							a Vault Administrator for the specified vault.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/360047137852-ELN-Entries-GET-POST-
		"""

		suffix = "/eln/entries"
		URL = self.URL + suffix

		data = {
				"title": title,
				"project": project,
				"eln_fields": eln_fields
		}

		response = self.sendPostRequest(URL, data)

		return response


	def postFiles(self, objectType, objectID, fileName):
		"""
		:Description: attach a file to an object (Run, Molecule, Protocol or ELN entry).

		:objectType (str): specifies the CDD object type to which the file will be attached.
						   Value must be one of: 'molecule', 'protocol', 'run', or 'eln_entry'.

		:objectID (int or str): an existing uid for a run, molecule, protocol, or ELN entry object.

		:fileName (str): path to a valid file for upload to CDD.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005739786-Files-GET-POST-DELETE-
		"""

		# Start w/ error-handling:

		validObjects = ["molecule", "protocol", "run", "eln_entry"]

		assert objectType in validObjects, f"\n'{objectType}' is not a valid CDD class object for attaching files.\nValid options include: {validObjects}."

		if not os.path.exists(fileName): raise FileNotFoundError(fileName)


		# Construct URL:

		suffix = "/files"
		URL = self.URL + suffix
		

		# Post file to CDD Vault + get response:
		# Does not use standard sendPostRequest() method, since request uses form-multipart.

		headers = {"X-CDD-Token": self.apiKey}

		files = {"file": (os.path.basename(fileName), open(fileName, "rb")),
				 "resource_class": (None, objectType),
				 "resource_id": (None, objectID)}

		response = requests.post(URL, headers=headers, files=files)
		
		response.raise_for_status()

		return response.json()
	

	@appendToDocString(helpDoc="post_inventory_samples.txt")
	def postInventorySamples(self, data):
		"""
		:Description: create a new Sample for a particular Batch ID. 
		
					  Note that the POST request must include a 'Credit' attribute indicating
					  the initial inventory amount in the Inventory Sample Event information.

		:data: Must be either a valid json object or a string file path to a valid json file.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/20703796893332-Inventory-Samples-GET-POST-PUT-
		"""

		# Construct URL:

		suffix = "/inventory_samples"
		URL = self.URL + suffix
		

		# Post inventory sample to CDD Vault + get response:

		response = self.sendPostRequest(URL, data)

		return response


	@appendToDocString(helpDoc="post_molecules.txt")
	def postMolecules(self, data):
		"""
		:Description: registers a new molecule in CDD Vault.

		:data: Must be either a valid json object or a string file path to a valid json file.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-
		"""

		# Construct URL:

		suffix = "/molecules"
		URL = self.URL + suffix
		

		# Post molecule to CDD Vault + get response:

		response = self.sendPostRequest(URL, data)

		return response
	

	def postSlurpsData(self, fileName, project, mappingTemplate=None, runs=None, autoreject=None, ambiguous_events_resolution=None, suspicious_events_resolution=None, interval=5.0):
		"""
		:Description: bulk import for programmatically importing data into CDD Vault. Uses an existing mapping template to map the data in the
					  import file into CDD Vault. Once a file has been uploaded through the API, data from the import is committed immediately 
					  unless there are errors or warnings. Any import errors or warnings (Suspicious Events) will cause the import to be REJECTED.

		:project (int or str): required. Either the name or id of a single project. Names should be passed as strings and id's should be
							   passed as integers.

		:mapping_template (int or str): optional. The name or id of a mapping template that matches the attached file. If not provided, 
										a mapping template that matches the file will be used. If there is more than one matching template, 
										an error will be raised. Similar to projects - names should be passed as strings and id's as integers. 

										See getMappingTemplates() method for a list of available mapping templates in the current vault.

		:runs (dict): a single run detail object which will be applied to all new runs present in the file.

						Valid keys include:

							:run_date: use YYYY-MM-DDThh:mm:ss:hh:mm. Default is today's date.

							:place: this field is called 'lab' within the CDD Vault web interface. No default value provided.

							:person: default value is user's full name.

							:conditions: no default value provided.

		:autoreject: optional. Designate if unresolved ambiguous events, suspicious events, or errors will cause the import to be automatically 
						rejected (default behaviour) or be left active in the Import Data tab for the user to resolve within the interface.
		
		:ambiguous_events_resolution (str): 
						Valid options:
							: "none" :  Default Do not resolve ambiguous events. See autoreject parameter for behavior.
							: "reject" : Automatically reject all ambiguous events.
							: "new_molecule" : Automatically create new molecules for all ambiguous events.
							: "new_batch" : Automatically create new batches on the first matching molecule for all ambiguous events.

		:suspicious_events_resolution (str): 
						Valid options:
							: "none" : Default Do not resolve suspicious events. See autoreject parameter for behavior.
							: "reject" : Automatically reject all suspicious events.
							: "accept" : Automatically accept all suspicious events.


		Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685526-Slurps-Post-i-e-Bulk-Import-of-Data-via-Files
		"""

		# Read-in file prm for import:
		
		files = {
				"file": (os.path.basename(fileName), open(fileName, "rb"))
				}

		# Read-in json prm for import:

		jsonObj = {"project": project}

		if mappingTemplate: jsonObj["mapping_template"] = mappingTemplate
		if runs: 
			
			validKeys = ["run_date", "place", "person", "conditions"]
			for k in runs: 
				
				assert k in validKeys, f"'{k}' is not a valid key for a run detail object."

			jsonObj["runs"] = runs

		if autoreject:
			jsonObj["autoreject"] = autoreject
		if ambiguous_events_resolution:
			jsonObj["ambiguous_events_resolution"] = ambiguous_events_resolution
		if suspicious_events_resolution:
			jsonObj["suspicious_events_resolution"] = suspicious_events_resolution
			
		jsonObj = json.dumps(jsonObj)


		# Send request to initiate bulk upload:

		suffix = "/slurps"
		URL = self.URL + suffix

		headers = {"X-CDD-Token": self.apiKey}

		response = requests.post(URL, headers=headers, files=files, data={"json": jsonObj})

		response.raise_for_status()


		# Check status of bulk upload until completed:

		slurpID = response.json()["id"]
		state = response.json()["state"]

		URL = self.URL + f"/slurps/{slurpID}"

		while state not in ["committed", "canceled", "rejected", "invalid"]:

			time.sleep(interval)

			exportResponse = requests.get(URL, headers=headers).json()
			state = exportResponse["state"]
			
		assert state == "committed", exportResponse


		# Get protocol + run information for successful imports using slurps ID:

		URL = self.URL + f"/protocols?slurp={slurpID}"

		outputResponse = requests.get(URL, headers=headers)
		
		outputResponse.raise_for_status()

		return outputResponse.json()


	def sendPutRequest(self, URL, jsonObj):
		"""
		:Description: general method for sending PUT requests to CDD vault.

					  'jsonObj' must either be a valid json object, or a string
					  file path pointing to a valid json file.

		"""

		if isinstance(jsonObj, str):

			jsonObj = json.load(open(jsonObj, "r"))

		
		headers = {"X-CDD-Token": self.apiKey}

		response = requests.put(URL, headers=headers, json=jsonObj)

		response.raise_for_status()
		
		return response.json()


	@appendToDocString(helpDoc="post_batches.txt") # Calls help from postBatches() method, since inputs are the same.
	def putBatches(self, id, data):
		"""
		:Description: update an existing batch. 

		:id (int or str): unique id for an existing batch object in CDD Vault.
						  Required, unless 'help' is set to True.

		:data: Must be either a valid json object, or a string file path to a valid json file. 

			   Fields not specified in the JSON are not changed. See postBatches() method for valid fields.
			   An exception to this is the Molecule field - putBatches() method call should not be used to update 
			   the chemical structure of the parent Molecule. Instead, use the putMolecules() method to achieve this.
			   Required, unless 'help' is set to True. 

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-#update
		"""

		# Construct URL:
	
		suffix = f"/batches/{id}"
		URL = self.URL + suffix
		

		# Put batch to CDD Vault + get response:

		response = self.sendPutRequest(URL, data)

		return response   


	@appendToDocString(helpDoc="put_eln_entries.txt")
	def putELNEntries(self, entryID, data):
		"""
		:Description: update the contents of an existing ELN entry.

					  Includes: 
					  	
						updating the title, project, ELN fields and even the body.
						adding links, text, and files using the 'append_to_body' parameter.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/360047137852-ELN-Entries-GET-PUT-POST-
		"""

		# Construct URL:
	
		suffix = f"/eln/entries/{entryID}"
		URL = self.URL + suffix
		

		# Put updated ELN entry to CDD Vault + get response:

		response = self.sendPutRequest(URL, data)

		return response   


	def putInventorySamples(self, sampleID, data):
		"""
		:Description: update an existing Sample with a new Sample Inventory Event row.

		:sampleID (int or str): unique ID of the inventory sample to update.

		:data: must be either a valid json object, or a string file path to a valid json file. 

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/20703796893332-Inventory-Samples-GET-POST-PUT-
		"""

		suffix = f"/inventory_samples/{sampleID}"
		URL = self.URL + suffix

		response = self.sendPutRequest(URL, data)

		return response


	@appendToDocString(helpDoc="put_molecules.txt")
	def putMolecules(self, id, data):
		"""
		:Description: update an existing molecule. Some keys behave differently when used with
					  putMolecules() vs. postMolecules(). Run with help=True for more details.

		:id (int or str): unique id for an existing molecule object in CDD Vault.
						  Required, unless 'help' is set to True.

		:data: Must be either a valid json object, or a string file path to a valid json file. 
			   Fields not specified in the JSON are not changed. See postMolecules() method for valid fields.
			   Required, unless 'help' is set to True. 

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-#update
		"""

		# Construct URL:
	
		suffix = f"/molecules/{id}"
		URL = self.URL + suffix
		

		# Put molecule to CDD Vault + get response:

		response = self.sendPutRequest(URL, data)

		return response   


	@appendToDocString(helpDoc="put_plates.txt")
	def putPlates(self, id, data):
		"""
		:Description: update an existing plate in CDD Vault.

		:id (int or str): unique id for an existing plate object in CDD Vault.

		:data: Must be either a valid json dictionary object, or a string file path to a valid json file. 
			   See the 'valid CDD Keyword arguments' in help for a list of valid keys to pass.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005739586-Plate-s-GET-POST-PUT-DELETE-
		"""

		# Construct URL:
	
		suffix = f"/plates/{id}"
		URL = self.URL + suffix
		

		# Put plate to CDD Vault + get response:

		response = self.sendPutRequest(URL, data)

		return response   


	def putReadoutRows(self, id, data):
		"""
		:Description: update an existing readout row (including the ability to flag an existing readout row as an outlier).

					  Allows a user to update a specified row of Protocol data, set its value to null, or flag a specified 
					  row of Protocol data as an outlier.

					  Use getProtocolData() method with runs specified to ascertain the id of the readout row for the Protocol data you wish to edit.
					  Use getProtocols() method to ascertain the readout definition IDs.
					  

		:id (int or str): unique id for an existing readout row object in CDD Vault.
						  Required, unless 'help' is set to True.

		:data: Must be either a valid json object, or a string file path to a valid json file. 

			   :Example Usage: { 
							"readouts": { 
							"283130": {"value": ">99"}, 
							"283131": {"value": 77},
							"283132": {"value": null},
							"283133": {"outlier": true}} 
							}

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/360059600831-Readout-Rows-PUT-DELETE-#update
		"""

		# Construct URL:
	
		suffix = f"/readout_rows/{id}"
		URL = self.URL + suffix
		

		# Put readout row to CDD Vault + get response:

		response = self.sendPutRequest(URL, data)

		return response   
	

	def putRuns(self, id, data):
		"""
		:Description: update an existing run. 

		:id (int or str): unique id for an existing run object in CDD Vault.

		:data: Must be either a valid json object, or a string file path to a valid json file. 

			   Fields not specified in the JSON are not changed. Allows users to update the run Project association 
			   and the Run_Date, Person, Place, and Conditions fields. Required, unless 'help' is set to True. 

			   Example Value:

					{
						"project":"New Project",
						"run_date":"2020-09-14",
						"conditions":"New Condition",
						"place":"New Lab",
						"person":"New Person"
					}

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/360024315171-Run-s-GET-PUT-DELETE-#update
		"""

		# Construct URL:
	
		suffix = f"/runs/{id}"
		URL = self.URL + suffix
		

		# Put run to CDD Vault + get response:

		response = self.sendPutRequest(URL, data)

		return response   
 

	def sendDeleteRequest(self, URL):

		headers = {"X-CDD-Token": self.apiKey}
		response = requests.delete(URL, headers=headers)

		response.raise_for_status()
		
		return response.json()


	def deleteBatchMoveJob(self, batchMoveJobID):
		"""
		:Description: cancels a single batch move job. Cannot be used to cancel a job already in progress.

		:batchMoveJobID (int or str): the unique ID of the batch move job to delete.
		"""

		# Construct URL: 

		suffix = f"/batch_move_jobs/{batchMoveJobID}"
		URL = self.URL + suffix

		# Delete batch move job present in CDD Vault + get response:

		response = self.sendDeleteRequest(URL)

		return response


	def deleteBatches(self, id):
		"""
		:Description: delete a batch present in CDD Vault.

					  Note that for safety/security purposes, batches which have data associated with them cannot be deleted 
					  via this method call. Data (such as rows of readout data in a Protocol Run) must be removed prior to using 
					  this method call to delete a Batch.
		
		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-#update
		"""

		# Note that batch deletes are actually performed using PUT requests, which must be submitted with an empty
		# projects array for the specified batch id.

		return self.putBatches(id, data={"projects": []})


	def deleteCollections(self, id):
		"""
		:Description: delete the collection as specified by its unique ID from CDD Vault.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/18707906579604-Collection-s-GET-POST-PUT-DELETE-
		"""

		# Construct URL:

		suffix = f"/collections/{id}"
		URL = self.URL + suffix

		# Delete collection from CDD Vault + retrieve response:
		
		response = self.sendDeleteRequest(URL)
		
		return response


	def deleteExport(self, id):
		"""
		:Description: delete an in-progress asynchronous export.

					  Primarily used during keyboard interrupts in the
					  getAsyncExport() method.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685506-Async-Export-GET-DELETE-
		"""

		# Construct URL:

		suffix = f"/exports/{id}"
		URL = self.URL + suffix
		
		# Delete running asynchronous export in CDD Vault + retrieve response:
		
		response = self.sendDeleteRequest(URL)
		
		return response


	def deleteFiles(self, fileID):
		"""
		:Description: delete a single file attached to an object (Run, Molecule, Protocol or ELN entry)
					  using its unique file ID.

		:fileID (int or str): unique ID for an existing file in CDD vault.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005739786-Files-GET-POST-DELETE-
		"""

		# Construct URL:

		suffix = f"/files/{fileID}"
		URL = self.URL + suffix
		
		# Delete file present in CDD Vault + get response:
		
		response = self.sendDeleteRequest(URL)
		
		return response


	def deleteMolecules(self, id):
		"""
		:Description: delete a molecule present in CDD Vault.
		
		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-#update
		"""

		# Note that molecule deletes are actually performed using PUT requests, which must be submitted with an empty
		# projects array for the specified molecule id.

		return self.putMolecules(id, data={"projects": []})


	def deletePlates(self, id):
		"""
		:Description: delete a single existing plate in CDD Vault using its plate ID.

		:id (int or str): unique ID for an existing plate in CDD vault.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005739586-Plate-s-GET-DELETE-#delete
		"""

		# Construct URL:

		suffix = f"/plates/{id}"
		URL = self.URL + suffix
		
		# Delete plate present in CDD Vault + get response:
		
		response = self.sendDeleteRequest(URL)
		
		return response


	def deleteReadoutRows(self, id):
		"""
		:Description: delete a single readout row associated with protocol data in CDD Vault using its unique ID.

		:id (int or str): unique ID for an existing readout row in CDD vault.

		:Reference: https://support.collaborativedrug.com/hc/en-us/articles/360059600831-Readout-Rows-PUT-DELETE-#delete
		"""

		# Construct URL:

		suffix = f"/readout_rows/{id}"
		URL = self.URL + suffix
		
		# Delete a single readout row of protocol data + get response:
		
		response = self.sendDeleteRequest(URL)
		
		return response


	def deleteRuns(self, id, slurps=False):
		"""
		:Description: either deletes a single run from CDD vault or delete all runs associated with a 
					  single slurps upload.

		:id (int or str): must be either an existing run ID if slurps=False, otherwise a valid slurps ID.

		:slurps (bool): if True, id will be interpreted as a slurps ID. Specifies the slurp_id of an import operation.
						All runs associated with the slurps ID will be deleted if the user has permissions for all runs. If not, no runs will be deleted.

		Reference: https://support.collaborativedrug.com/hc/en-us/articles/360024315171-Run-s-GET-PUT-DELETE-
		"""
		
		# Construct URL:

		if slurps: suffix = f"/runs?slurp={id}"
		else: suffix = f"/runs/{id}"

		URL = self.URL + suffix

		# Delete runs present in CDD Vault + get response:
		
		response = self.sendDeleteRequest(URL)
		
		return response

