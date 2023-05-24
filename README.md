# CDD-Python-SDK


### A Python client for streamlined execution of [CDD Vault API methods](https://support.collaborativedrug.com/hc/en-us/sections/115001607043-API-Function-Calls).


- [Known Issues](#known-issues)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [VaultClient Attributes](#vaultclient-attributes)
- [VaultClient Methods](#vaultclient-methods)
	- [Control/Misc.](#controlmisc)
		- [Set the vault ID and construct the base URL, from which endpoints for all subsequent API calls (GET, POST, PUT, DELETE) will be constructed.](#set-the-vault-id-and-construct-the-base-url-from-which-endpoints-for-all-subsequent-api-calls-get-post-put-delete-will-be-constructed)
		- [Set the API token credentials, which will be passed in the request header to CDD Vault with each API request.](#set-the-api-token-credentials-which-will-be-passed-in-the-request-header-to-cdd-vault-with-each-api-request)
		- [Set the 'maxSyncObjects' attribute, which is used to determine when a synchronous vs asynchronous export request is submitted to CDD. If the # of objects returned from a GET request is ever `>=` maxSyncObjects, the call will be repeated asynchronously.](#set-the-maxsyncobjects-attribute-which-is-used-to-determine-when-a-synchronous-vs-asynchronous-export-request-is-submitted-to-cdd-if-the--of-objects-returned-from-a-get-request-is-ever--maxsyncobjects-the-call-will-be-repeated-asynchronously)
	- [Batches](#batches)
		- [Return a set or subset of batches from CDD vault.](#return-a-set-or-subset-of-batches-from-cdd-vault)
		- [Create a new batch in CDD Vault.](#create-a-new-batch-in-cdd-vault)
		- [Update an existing batch in CDD Vault.](#update-an-existing-batch-in-cdd-vault)
	- [Molecules](#molecules)
		- [Return a list of molecules and their batches, based on optional parameters.](#return-a-list-of-molecules-and-their-batches-based-on-optional-parameters)
		- [Register a new molecule in CDD Vault.](#register-a-new-molecule-in-cdd-vault)
		- [Update an existing molecule in CDD Vault.](#update-an-existing-molecule-in-cdd-vault)
	- [Public Data-Sets](#public-data-sets)
		- [Return a list of accessible public data sets for the given vault.](#return-a-list-of-accessible-public-data-sets-for-the-given-vault)
	- [ELN Entries](#eln-entries)
		- [Return information on the ELN entries for the specified vault](#return-information-on-the-eln-entries-for-the-specified-vault)
		- [Create a new ELN entry.](#create-a-new-eln-entry)
	- [Fields](#fields)
		- [Return a list of available fields for the given vault.](#return-a-list-of-available-fields-for-the-given-vault)
	- [Files](#files)
		- [Retrieve a single file object from CDD Vault using its file ID.](#retrieve-a-single-file-object-from-cdd-vault-using-its-file-id)
		- [Attach a file to an object (Run, Molecule, Protocol or ELN entry).](#attach-a-file-to-an-object-run-molecule-protocol-or-eln-entry)
		- [Delete a single file attached to an object (Run, Molecule, Protocol or ELN entry) using its unique file ID.](#delete-a-single-file-attached-to-an-object-run-molecule-protocol-or-eln-entry-using-its-unique-file-id)
	- [Mapping Templates](#mapping-templates)
		- [Return summary information on all available mapping templates in the Vault specified. Alternatively, if 'id' argument is set, will retrieve details on the data objects mapped within a specific mapping template.](#return-summary-information-on-all-available-mapping-templates-in-the-vault-specified-alternatively-if-id-argument-is-set-will-retrieve-details-on-the-data-objects-mapped-within-a-specific-mapping-template)
	- [Plates](#plates)
		- [Return a collection of plates from CDD vault.](#return-a-collection-of-plates-from-cdd-vault)
		- [Delete a single existing plate in CDD Vault using its plate ID.](#delete-a-single-existing-plate-in-cdd-vault-using-its-plate-id)
	- [Plot](#plot)
		- [Download dose-response curves/plots for a single Batch.](#download-dose-response-curvesplots-for-a-single-batch)
	- [Projects](#projects)
		- [Return a list of accessible projects for the given vault.](#return-a-list-of-accessible-projects-for-the-given-vault)
	- [Protocols](#protocols)
		- [Return a list of accessible projects for the given vault.](#return-a-list-of-accessible-projects-for-the-given-vault-1)
	- [Protocol Data](#protocol-data)
		- [Return a filtered subset of the readout data for a single protocol using its protocol ID.](#return-a-filtered-subset-of-the-readout-data-for-a-single-protocol-using-its-protocol-id)
	- [Readout Rows](#readout-rows)
		- [Update an existing readout row (including the ability to flag an existing readout row as an outlier).](#update-an-existing-readout-row-including-the-ability-to-flag-an-existing-readout-row-as-an-outlier)
		- [Delete a single readout row associated with protocol data in CDD Vault using its unique ID.](#delete-a-single-readout-row-associated-with-protocol-data-in-cdd-vault-using-its-unique-id)
	- [Runs](#runs)
		- [Retrieve a single run using its unique run ID.](#retrieve-a-single-run-using-its-unique-run-id)
		- [Update an existing run using its unique run ID.](#update-an-existing-run-using-its-unique-run-id)
		- [Delete one or more runs from CDD Vault](#delete-one-or-more-runs-from-cdd-vault)
	- [Slurps](#slurps)
		- [Bulk import endpoint for programmatic use. CDD Support Topic](#bulk-import-endpoint-for-programmatic-use-cdd-support-topic)


# Known Issues


  - Molecules: finish adding help documentation for query parameters.


* * *
# Installation

To install, run the following in a Git terminal:

```bash
git clone https://github.com/Workflow-Informatics/CDD-Python-SDK.git
cd CDD-Python-SDK/
python setup.py install
```
***
# Getting Started

1. Import the `VaultClient` module:

```python
from cdd.VaultClient import VaultClient
```
2. Confirm your [User Permissions](https://support.collaborativedrug.com/hc/en-us/articles/214359023-Vault-User-Roles), then instantiate a VaultClient to work with your data:
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

4. A full list of valid CDD API query parameters can be displayed in each method's doc string.
```python
vault.getMolecules?
```
***


# VaultClient Attributes

`self.URL` Returns the URL assciated with the active VaultClient instance

`self.vaultNum` Returns the four-digit vault ID associated with the active VaultClient instance

`self.apiKey` Returns the API Key associated with the active VaultClient instance

`self.maxSyncObjects` Returns the current value of the maxSyncObjects attribute


# VaultClient Methods
*Note: Additional methods are defined for VaultClient, but are not intended to be called by the end-user. However, developers are encouraged to check the docstrings within those methods.*

## Control/Misc.

```python
setVaultNumAndURL(vaultNum)
```
### Set the vault ID and construct the base URL, from which endpoints for all subsequent API calls (GET, POST, PUT, DELETE) will be constructed.
* __Returns__: `tuple` a two-element tuple consisting of the vault ID and the base URL for accessing the CDD Vault API.

```python
setAPIKey(apiKey)
```
### Set the API token credentials, which will be passed in the request header to CDD Vault with each API request. 

	Note that the API token must have read/write access to the vault specified by the vault ID when executing the various API calls or an error will be returned.
* __Returns__: `str`

```python
setMaxSyncObjects(value=1000)
```
### Set the 'maxSyncObjects' attribute, which is used to determine when a synchronous vs asynchronous export request is submitted to CDD. If the # of objects returned from a GET request is ever `>=` maxSyncObjects, the call will be repeated asynchronously.

	Defaults to 1000, the maximum # of objects which a CDD GET request can return synchronously.

Only used in methods where GET requests can be performed asynchronously: 
	
	Molecules, Batches, Plates, Protocols, and Protocol Data. See method sendSyncAndAsyncGets().
* __Returns__: `int`


## Batches
```python
getBatches(asDataFrame=True, **kwargs)
```
### Return a set or subset of batches from CDD vault.

 * __asDataFrame `bool`__ returns the json as a Pandas DataFrame.

__Additional Valid Arguments__:
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
postBatches(data=None)
```
### Create a new batch in CDD Vault.

* __data__: Required. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON Examples](https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-#create)

```python
putBatches(self, id=None, data=None) 
# id (int or str): unique id for an existing batch object in CDD Vault.
```
### Update an existing batch in CDD Vault.

* __data__: Required. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON Examples](https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-#update)

		Note: putBatches() method call should not be used to update the chemical structure of the parent Molecule. 
		
		Instead, use the putMolecules() method to achieve this.
	

## Molecules


```python
getMolecules(self, asDataFrame=True, help=False, **kwargs)
```
### Return a list of molecules and their batches, based on optional parameters.

 * __asDataFrame `bool`__ returns the json as a Pandas DataFrame.

__Additional Valid Arguments__:
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
### Register a new molecule in CDD Vault.

- __data__: Required, unless 'help' is set to True. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON](https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-#create)

```python
putMolecules(id=None, data=None, help=False)
```

### Update an existing molecule in CDD Vault.

 * id `int` or `str` unique id for an existing molecule object in CDD Vault. Required, unless 'help' is set to True.

* __data__: Required, unless 'help' is set to True. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON](https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-#update)


## Public Data-Sets


```python
getDatasets(asDataFrame=True)
```
### Return a list of accessible public data sets for the given vault.

	Defaults to 1000, the maximum # of objects which a CDD GET request can return synchronously.
	
__Returns__: `pandas.DataFrame` or `list` 


## ELN Entries
*Note: For security purposes, the GET and POST ELN Entries CDD Vault API commands documented here are only available for Vault Administrators.*


```python
getELNEntries(summary=True, asDataFrame=True, exportPath=None, unzipELNEntries=False, help=False, **kwargs)
```
### Return information on the ELN entries for the specified vault

* __summary `bool`__: if true, returns summary data for the requested ELN entries. This is equivalent to the synchronous call.

* __asDataFrame `bool`__: returns the summary as a Pandas DataFrame. Only relevant if `summary=True`.

* __exportPath `str`__: file path for extracting zipped ELN entries to. Only relevant if `summary=False`.

* __unzipELNEntries `bool`__: if true, extracts the zip contents of exportPath to a directory named `\exportPath\`
	
__Returns__: `pandas.DataFrame` or `list` 


```python
postELNEntries(project, title=None, eln_fields={})
```
### Create a new ELN entry.

* __project `str`__ the project ID or name where the new ELN entry will be created.

* __title `str`__ the title of the new ELN entry.

* __eln_fields `dict`__ a set of configured ELN field/value pairs which have been set by a Vault Administrator for the specified vault.


## Fields


```python
getFields(asDataFrame=True)
```
### Return a list of available fields for the given vault.

	This API call will provide you with the “type” and “name” values of *all* fields within a Vault. 
	The json keys returned by this API call are organized into the following: internal, batch, molecule, protocol
	
 * __asDataFrame `bool`__ returns the json as a Pandas DataFrame.

__Returns__: `dict` of `pandas.DataFrame` or `list` 


## Files


```python
getFile(fileID, destFolder=None)
```
### Retrieve a single file object from CDD Vault using its file ID.

 * __destFolder `str`__ destination folder where file contents should be written to. File name will default to the original name of the file when it was uploaded to CDD Vault.
	
__Returns__: `str` of decoded response, also writes to file system.


```python
postFiles(objectType, objectID, fileName)
```
### Attach a file to an object (Run, Molecule, Protocol or ELN entry).

 * __objectType `str`__ specifies the CDD object type to which the file will be attached. Value must be one of *molecule*, *protocol*, *run*, or *eln_entry*.
	
* __objectID `str`__ an existing uid for a run, molecule, protocol, or ELN entry object.

* __fileName `str`__ valid file path for upload to CDD.


```python
deleteFiles(fileID)
```
### Delete a single file attached to an object (Run, Molecule, Protocol or ELN entry) using its unique file ID.

* __fileID `str`__ unique ID for an existing file in CDD vault.


## Mapping Templates


```python
getMappingTemplates(id=None, asDataFrame=True)
```
### Return summary information on all available mapping templates in the Vault specified. Alternatively, if 'id' argument is set, will retrieve details on the data objects mapped within a specific mapping template.

Additional fields when __id__ argument is set include:

	A 'header_mappings' section that identifies the field/readout each header is mapped to.

	A 'file' section that provides details on the original file used to create the template.

 * __asDataFrame `bool`__ returns the json as a Pandas DataFrame. This parameter is ignored if an __id__ value has been set.
	
__Returns__: JSON `dict` or `pandas.DataFrame`


## Plates


```python
getPlates(asDataFrame=True, help=False, **kwargs)
```
### Return a collection of plates from CDD vault.

 * __asDataFrame `bool`__ returns the json as a Pandas DataFrame. This parameter is ignored if an __id__ value has been set.

 __Additional Valid Arguments__:
```json
"plates": "Comma-separated list of ids.",
			
"names": "Comma-delimited list of plate names.",

"locations": "Comma-delimited list of plate locations.",

"async": "Boolean. If true, do an asynchronous export (see Async Export). Use for large data sets. Note - always set to True when using Python API",

"page_size": "The maximum # of objects to return.",

"projects": "Comma-separated list of project ids.Defaults to all available projects.Limits scope of query."
```
	
__Returns__: JSON `dict` or `pandas.DataFrame`


```python
deletePlates(id)
```
### Delete a single existing plate in CDD Vault using its plate ID.

* __id `str` or `int`__ Unique ID for an existing plate in CDD vault.


## Plot


```python
getPlot(batchID, protocolID, size="small", destFolder=None)
```
### Download dose-response curves/plots for a single Batch. 

	This API call generates a png image file containing the dose-response plot for the specific Batch within the specified Protocol

 * __batchID `str`__ id for the desired batch.

 * __protocolID `str`__ id for the desired protocol

 * __size `str`__ relative size of the response png file. Valid options are *small*, *medium* and *large*

 * __destFolder `str`__ destination folder where file contents should be written to. File name will default to the original name of the file when it was uploaded to CDD Vault.
	
__Returns__: `str` of decoded response, also writes to file system.


## Projects


```python
getProjects(asDataFrame=True)
```
### Return a list of accessible projects for the given vault.

 * __asDataFrame `bool`__ returns the json as a Pandas DataFrame.
	
__Returns__: JSON `dict` or `pandas.DataFrame`


## Protocols


```python
getProtocols(asDataFrame=True, help=False, **kwargs)
```
### Return a list of accessible projects for the given vault.

 * __asDataFrame `bool`__ returns the json as a Pandas DataFrame.

 __Additional Valid Arguments__:
```json
"protocols": "Comma-separated list of protocol ids. Cannot be used with other parameters",

"names": "Comma-separated list of protocol names. Cannot be used with other parameters.",

"only_ids": "Boolean. If true, only the Protocol IDs are returned,\n" 
"allowing for a smaller and faster response. Default: false",

"created_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"created_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"modified_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"modified_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"runs_modified_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
"runs_modified_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",

"plates": "Comma-separated list of plate ids.",

"molecules": "Comma-separated list of molecule ids.",

"page_size": "The maximum # of objects to return.",

"projects": "Comma-separated list of project ids.\n"
"Defaults to all available projects.\n"
"Limits scope of query.",

"data_sets": "Comma-separated list of public data set ids.\n"
"Defaults to no data sets. Limits scope of query.",

"slurp": "Specify the slurp_id of an import operation.\n"
"Once an import has been committed, you can return\n" 
"additional JSON results that will expose the Protocol\n" 
"and Run(s) of data that were imported."
```
	
__Returns__: JSON `dict` or `pandas.DataFrame`



## Protocol Data

```python
getProtocolData(id=None, asDataFrame=True, help=False, statusUpdates=True, **kwargs)
```
### Return a filtered subset of the readout data for a single protocol using its protocol ID. 
	
	'id' argument is required, unless 'help' is set to True.

 * __id `str` or `int`__ ID for the desired protocol.

 * __asDataFrame `bool`__ Returns the json as a Pandas DataFrame.

 * __statusUpdates `bool`__ Display status updates for the asynchronous export.

 __Additional Valid Arguments__:
```json
"plates": "Comma-separated list of plate ids. Include only data for the specified plates.",

"molecules": "Comma-separated list of molecule ids. Include only data for the specified molecules.",

"runs_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm). Include only data for runs on or before the date",

"runs_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm). Include only data for runs on or after the date.",

"runs": "Comma-separated list of run ids for the given protocol. Include only data for runs listed.",

"page_size": "The maximum # of objects to return.",

"projects": "Comma-separated list of project ids. Defaults to all available projects. Limits scope of query.",

"format": "'csv'
			Generates a csv file which mimics the file generated when you choose the 'Export readouts' button 
			from the Run-level 'Run Details' tab within the CDD Vault web interface.
			When used as a keyword argument, this forces an asynchronous GET request.
			All other keyword arguments will be ignored, EXCEPT for the 'runs' keyword."
```
__Returns__: JSON `dict` or `pandas.DataFrame`. Optionally writes .csv to file system.


## Readout Rows

```python
putReadoutRows(id=None, data=None, help=False)
```
### Update an existing readout row (including the ability to flag an existing readout row as an outlier).

	Allows a user to update a specified row of Protocol data, set its value to null, or flag a specified row of Protocol data as an outlier.

	Use getProtocolData() method with runs specified to ascertain the id of the readout row for the Protocol data you wish to edit.
	
	Use getProtocols() method to ascertain the readout definition IDs.

 * __id `str` or `int`__ unique id for an existing readout row object in CDD Vault. Required, unless 'help' is set to True.
 
 * __data__: Required, unless 'help' is set to True. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON Examples](https://support.collaborativedrug.com/hc/en-us/articles/360059600831-Readout-Rows-GET-PUT-DELETE-#update)


```python
deleteReadoutRows(id)
```
### Delete a single readout row associated with protocol data in CDD Vault using its unique ID.

 * __id `str` or `int`__ unique id for an existing readout row object in CDD Vault.



## Runs

```python
getRun(runID)
```
### Retrieve a single run using its unique run ID.

 * __id `str` or `int`__ unique id for an existing readout row object in CDD Vault.


```python
putRuns(id=None, data=None, help=False)
```
### Update an existing run using its unique run ID.

 * __id `str` or `int`__ unique id for an existing run object in CDD Vault.

  * __data__: Required, unless 'help' is set to True. Must be either a valid json object, or a string file path to a valid json file. [Allowed JSON Examples](https://support.collaborativedrug.com/hc/en-us/articles/360024315171-Run-s-GET-PUT-DELETE-#update)

		Fields not specified in the JSON are not changed. 
		
		Allows users to update the run's Project association,
			as well as the Run_Date, Person, Place, and Conditions fields. 
		
		Required, unless 'help' is set to True. 

```python
deleteRuns(id, slurps=False)
```
### Delete one or more runs from CDD Vault

 * __slurps `bool`__ If True, the id parameter will be interpreted as a [slurps ID](https://support.collaborativedrug.com/hc/en-us/articles/115005685526-Slurps-Post-i-e-Bulk-Import-of-Data-via-Files). Specifies the slurp_id of an import operation. The user must have [appropriate permissions](https://support.collaborativedrug.com/hc/en-us/articles/214359023-Vault-User-Roles) to remove ALL runs in the slurp.
		
		All runs associated with the slurps ID will be deleted. 
		
		If user permissions are insufficient, no runs will be deleted.
 
 * __id `str` or `int`__ unique id for an existing readout row object in CDD Vault.


 ## Slurps

 ```python
postSlurpsData(fileName, project, mappingTemplate=None, runs=None, interval=5.0)
```

### Bulk import endpoint for programmatic use. [CDD Support Topic](https://support.collaborativedrug.com/hc/en-us/articles/115005685526-Slurps-Post-i-e-Bulk-Import-of-Data-via-Files)

	Uses an existing mapping template to map the data in the import file into CDD Vault.
	
	Once a file has been uploaded through the API, data from the import is committed immediately unless there are errors or warnings.
	
	Any import errors or warnings (Suspicious Events) will cause the import to be REJECTED.

 * __project `str` or `int`__ Required. Either the name or id of a single project. To use a project name, enter a `str`. To use a project id, enter an `int`.

 * __mapping_template `str` or `int`__ The name (`str`) or id (`int`) of a mapping template that matches the attached file. If you choose to exclude this keyword:
 
 		CDD will attempt to use an existing template that matches the import file.

		If none of the templates in your vault match, the import will be REJECTED

		If more than one of the templates in your vault match, the import will be REJECTED
 
 * __runs `dict`__ Optional. a single run detail object which will be applied to all new runs present in the file. Valid Keys:
 ```json
"run_date": use YYYY-MM-DDThh:mm:ss:hh:mm. Default is today’s date.
"place": This is the 'lab' condition in CDD. No default.
"person": default value is user's full name.
"conditions": no default value provided.
```
