"""
:Description: A high-level class wrapping VaultClient.
"""

from .VaultClient import VaultClient


class Vault(VaultClient):


	def getReadoutIDsFromNames(self, protoID, targetNames):
		"""
		:Description: returns a dictionary mapping a list of input readout names
					  for a specified protocol to their corresponding readout
					  ID's.

		:protoID (int or str): the unique protocol ID to which the readoutNames
							   in the 'targetNames' arg belong.

		:targetNames (list): a list of readout names which will be mapped to
							 their corresponding readout ID's.

		:return (dict):
		"""

		targetNames = set(targetNames)

		readoutDefs = self.getProtocols(asDataFrame=False, protocols=protoID)
		readoutDefs = readoutDefs[0].get("readout_definitions")

		readoutDict = {r.get("name"): r.get("id") for r in readoutDefs}
		readoutDict = {k:v for k,v in readoutDict.items() if k in targetNames}

		for t in targetNames: readoutDict.setdefault(t, None)

		return readoutDict


	