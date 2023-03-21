__GET Methods to Implement:__

  - Molecules: finish adding help documentation for query parameters.
  - Plot: TBD
  - Saved Search: TBD

__POST Methods to Implement: done.__

__PUT Methods to Implement: done.__

__DELETE Methods to Implement: done.__

__QOL Changes__:

 - Set dataframe indexes based on responses 


# CDD-Python-API
### A Python client for rapid execution of [CDD Vault API methods](https://support.collaborativedrug.com/hc/en-us/sections/115001607043-API-Function-Calls).
* * *

# Installation

To install, run the following in a Git terminal:

```bash
git clone https://github.com/Workflow-Informatics/CDD-Python-API.git
cd CDD-Python-API/
python setup.py install
```
***
# Getting Started

1. Import the `VaultClient` module:

```python
from cdd.VaultClient import VaultClient
```
2. Instantiate a VaultClient to work with your data:
```python
vaultNum = 4598 # Insert your unique vault ID here.
apiToken = os.environ["cddAPIToken"] # Insert your API token here.

vault = VaultClient(vaultNum, apiToken)
```

3. Use the provided methods and properties to download, upload, and edit data:

```python
projects_dataframe = vault.getProjects() # default response is pandas dataframe
protocols_json = vault.getProtocols(asDataFrame=False)

filtered_protocols = vault.getProtocols(projects = projects_dataframe.at[0, 'id'])
```

4. A full list of valid parameters can be returned by passing  `help=True`
```python
vault.getMolecules(help=True)
```
***
# Index


## Control Attributes
```python
self.URL # returns the URL assciated with the active VaultClient instance

self.vaultNum # returns the four-digit vault ID associated with the active VaultClient instance

self.apiKey # returns the API Key associated with the active VaultClient instance

self.maxSyncObjects # returns the current value of the maxSyncObjects attribute
```


## Control Methods
*Note: Additional (internal) methods are defined for VaultClient. The methods in this list are intended to be called by the end user.*
```python
setVaultNumAndURL(vaultNum)
```
__Description__: Sets the vault ID and constructs the base URL, from which endpoints for all subsequent API calls (GET, POST, PUT, DELETE) will be constructed.
__Returns__: `tuple` a two-element tuple consisting of the vault ID and the base URL for accessing the CDD Vault API.

```python
setAPIKey(apiKey)
```
__Description__: Sets the API token credentials, which will be passed in the request header to CDD Vault with each API request. 

	Note that the API token must have read/write access to the vault specified by the vault ID when executing the various API calls or an error will be returned.
__Returns__: `str`

```python
setMaxSyncObjects(value=1000)
```
__Description__: Sets the 'maxSyncObjects' attribute, which is used to determine when a synchronous vs asynchronous export request is submitted to CDD. If the # of objects returned from a GET request is ever `>=` maxSyncObjects, the call will be repeated asynchronously.

	Defaults to 1000, the maximum # of objects which a CDD GET request can return synchronously.

Only used in methods where GET requests can be performed asynchronously: 
	
	Molecules, Batches, Plates, Protocols, and Protocol Data. See method sendSyncAndAsyncGets().
__Returns__: `int`


## Batches Methods
```python
getBatches(asDataFrame=True, help=False, **kwargs)
```
__Description__: Return a set or subset of batches from CDD vault.

__Valid Arguments__:
```json
"batches": "Comma-separated list of ids. Cannot be used with other parameters"

"no_structures": "Boolean. If true, omit structure representations for a smaller and faster response. Default: false",

"only_ids": "Boolean. If true, only the Batch IDs are returned, allowing for a smaller and faster response. Default: false",

"created_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"created_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"modified_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"modified_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"molecule_created_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"molecule_created_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",

"page_size": "The maximum # of objects to return.",

"projects": "Comma-separated list of project ids. Defaults to all available projects. Limits scope of query.",

"data_sets": "Comma-separated list of public data set ids. Defaults to no data sets. Limits scope of query.",

"molecule_batch_identifier": "A Molecule-Batch ID used to query the Vault. Use this parameter to limit the number of Molecule UDF Fields to return",

"molecule_fields": "Array of Molecule field names to include in the resulting JSON. Use this parameter to limit the number of Molecule UDF Fields to return.",

"batch_fields": "Array of Batch field names to include in the resulting JSON. Use this parameter to limit the number of Batch UDF Fields to return.",

"fields_search": "Array of Batch field names & values. Used to filter Batches returned based on query values"
```
__Returns__: `pandas.DataFrame` or `list`

```python
postBatches(data=None, help=False)
```
__Description__: Creates a new batch in CDD Vault.

* __data__: Required, unless 'help' is set to True. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON](https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-#create)

```python
putBatches(self, id=None, data=None, help=False) 
# id (int or str): unique id for an existing batch object in CDD Vault. Required, unless 'help' is set to True.
```
__Description__: Updates an existing batch in CDD Vault.

* __data__: Required, unless 'help' is set to True. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON](https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-#update)

	* An exception to this is the Molecule field - putBatches() method call should not be used to update 
	the chemical structure of the parent Molecule. 
	* Instead, use the putMolecules() method to achieve this.
	* Required, unless 'help' is set to True.
	

## Molecules Methods
```python
getMolecules(self, asDataFrame=True, help=False, **kwargs)
```
__Description__: Return a list of molecules and their batches, based on optional parameters.

__Valid Arguments__:
```json
"molecules": "Comma-separated list of ids (not molecule names!). Cannot be used with other parameters",

"names": "Comma-separated list of names/synonyms.",

"async": "Boolean. If true, do an asynchronous export (see Async Export). Use for large data sets. Note - always set to True when using Python API",

"no_structures": "Boolean. If true, omit structure representations for a smaller and faster response. Default: false",

"only_ids": "Boolean. If true, only the Molecule IDs are returned, allowing for a smaller and faster response. Default: false",

"created_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"created_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"modified_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"modified_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",

"batch_created_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"batch_created_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"batch_field_before_name": "Batch field name",
"batch_field_before_date": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"batch_field_after_name": "Batch field name",
"batch_field_after_date": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",

"page_size": "The maximum # of objects to return.",

"projects": "Comma-separated list of project ids. Defaults to all available projects. Limits scope of query.",

"data_sets": "Comma-separated list of public data set ids. Defaults to no data sets. Limits scope of query.",

"structure": "SMILES, cxsmiles or mol string for the query structure. Returns Molecules from the Vault that match the structure-based query submitted via this API call.",

"structure_search_type": "Available options are: 'exact', 'similarity' or 'substructure'. Default option is substructure.",

"structure_similarity_threshold": "A number between 0 and 1. Include this parameter only if the structure_search_type is 'similarity'.",

"inchikey": "A valid InchiKey. Use this parameter in place of the 'structure' and 'structure_search_type' parameters.",

"molecule_fields": "Array of Molecule field names to include in the resulting JSON. Use this parameter to limit the number of Molecule UDF Fields to return.",

"batch_fields": "Array of Batch field names to include in the resulting JSON. Use this parameter to limit the number of Batch UDF Fields to return.",

"fields_search": "Array of Molecule field names & values. Used to filter Molecules returned based on query values"
```
__Returns__: `pandas.DataFrame` or `list`

```python
postMolecules(data=None, help=False)
```
__Description__: Registers a new molecule in CDD Vault.

- __data__: Required, unless 'help' is set to True. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON](https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-#create)

```python
putMolecules(self, id=None, data=None, help=False)
# id (int or str): unique id for an existing molecule object in CDD Vault. Required, unless 'help' is set to True.
```
__Description__: Updates an existing batch in CDD Vault.

* __data__: Required, unless 'help' is set to True. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON](https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-#update)


## Public Data-Sets Methods


```python
getDatasets(asDataFrame=True)
```
__Description__: Returns a list of accessible public data sets for the given vault.

	Defaults to 1000, the maximum # of objects which a CDD GET request can return synchronously.
	
__Returns__: `pandas.DataFrame` or `list` 


## ELN Entries Methods
*Note: For security purposes, the GET and POST ELN Entries CDD Vault API commands documented here are only available for Vault Administrators.*


```python
getELNEntries(self, summary=True, asDataFrame=True, exportPath=None, unzipELNEntries=False, help=False, **kwargs)
```
__Description__: Returns information on the ELN entries for the specified vault

* __summary `bool`__: if true, returns summary data for the requested ELN entries. This is equivalent to the synchronous call.

* __asDataFrame `bool`__: returns the summary as a Pandas DataFrame. Only relevant if `summary=True`.

* __exportPath `str`__: file path for extracting zipped ELN entries to. Only relevant if `summary=False`.

* __unzipELNEntries `bool`__: if true, extracts the zip contents of exportPath to a directory named `\exportPath\`
	
__Returns__: `pandas.DataFrame` or `list` 


```python
postELNEntries(self, project, title=None, eln_fields={})
```
__Description__ creates a new ELN entry.

* __project `str`__ the project ID or name where the new ELN entry will be created.

* __title `str`__ the title of the new ELN entry.

* __eln_fields `dict`__ a set of configured ELN field/value pairs which have been set by a Vault Administrator for the specified vault.


## Fields Methods


```python
getFields(self, asDataFrame=True)
```
__Description__: returns a list of available fields for the given vault.

	This API call will provide you with the “type” and “name” values of *all* fields within a Vault. 
	The json keys returned by this API call are organized into the following: internal, batch, molecule, protocol
	
__Returns__: `dict` of `pandas.DataFrame` or `list` 