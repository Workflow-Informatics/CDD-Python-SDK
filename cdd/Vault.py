"""
:Description: A high-level class wrapping VaultClient.
"""

import pandas as pd

from .VaultClient import VaultClient


class Vault(VaultClient):

	def mapReadoutNamesToIDs(self, protoID, targetNames=None):
		"""
		:Description: returns a dictionary mapping a list of input readout names
					  for a specified protocol to their corresponding readout
					  ID's.

		:protoID (int or str): the unique protocol ID to which the readoutNames
							   in the 'targetNames' arg belong.

		:targetNames (list): a list of readout names which will be mapped to
							 their corresponding readout ID's. If targetNames
							 is None, a dictionary mapping all readout names
							 to ID's will be returned.

		:return (dict):
		"""

		readoutDefs = self.getProtocols(asDataFrame=False, protocols=protoID)
		readoutDefs = readoutDefs[0].get("readout_definitions")

		readoutDict = {r.get("name"): r.get("id") for r in readoutDefs}

		if targetNames is None: 
			
			return readoutDict

		targetNames = set(targetNames)

		readoutDict = {k:v for k,v in readoutDict.items() if k in targetNames}

		for t in targetNames: readoutDict.setdefault(t, None)

		return readoutDict


	def getFormattedRunData(self, protoID, runIDs=None, omitMetaCols=True, omitOutlierField=True):
		"""
		:Description: High-level method for simplifying usage of the VaultClient's 
					  getReadoutRows() method. 
					  
					  For a single readout row, by default all readout names/values are 
					  aggregated as a dictionary in a single DataFrame column.

					  Reformats the readouts column so that values for each unique readout name
					  are inserted into the DataFrame as a separate column.


		:protoID (int or str): unique protocol ID for which run data will be retrieved.

		:runIDs (list of int or str): a set of run ID's which limits the returned readouts
									  to the runs specified. Optional. If not included, all 
									  runs for the specified protocol ID will be returned.


		:omitMetaCols (bool or list of str): if true, removes extra metadata columns returned by CDD 
											 when retrieving readout data (Ex: creation date, class, etc.).

											 If a boolean value is provided, a set of default columns will
											 be removed from the returned DataFrame. 
											 
											 Alternatively, a list of string column names can be passed 
											 modifying which columns will be dropped from the returned DataFrame.


		:omitOutlierField (bool): if true, each readout column will only include the 'value'
								  field while omitting the 'outlier' field.

		:return (DataFrame):
		"""

		readoutDefs = self.mapReadoutNamesToIDs(protoID=protoID)
		readoutDefs = {v:k for k,v in readoutDefs.items()} # ID -> Name


		# Retrieves the readout data as list of dictionaries:

		if runIDs is None:
			readouts = self.getReadoutRows(protocols=protoID, asDataFrame=False)

		else:
			runIDs = ",".join([str(r) for r in runIDs])
			readouts = self.getReadoutRows(protocols=protoID, runs=runIDs, asDataFrame=False)


		# Separates the aggregated 'readouts' key for each row/dictionary into separate fields using
		# the readout names as keys:

		for r in readouts:

			formattedReadouts = r.pop("readouts")
			formattedReadouts = {readoutDefs.get(int(k)):v for k,v in formattedReadouts.items()}

			if omitOutlierField:

				formattedReadouts = {k:v.get("value") for k,v in formattedReadouts.items()}

			r.update(formattedReadouts)

		readouts = pd.DataFrame(readouts)


		# Omits extraneous metadata columns:

		if omitMetaCols:

			if isinstance(omitMetaCols, bool):

				omitMetaCols = [ # Default columns to remove.
							"class",
							"created_at",
							"modified_at",
							"type"
				]

			for c in omitMetaCols: readouts = readouts.drop(c, axis=1)

		return readouts