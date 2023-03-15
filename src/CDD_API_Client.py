'''
______________________________________________________________________________________________________________________________________________
Copyright © 2022 Workflow Informatics - Distribution of this software without written permission of Workflow Informatics is prohibited.

This SOFTWARE PRODUCT is provided by Workflow Informatics "as is" and "with all faults." 

Workflow Informatics makes no representations or warranties of any kind concerning the safety, suitability, inaccuracies, typographical errors, or other harmful components of this SOFTWARE PRODUCT. 

You are solely responsible for determining whether this SOFTWARE PRODUCT is compatible with your equipment and other software installed on your equipment.

You are solely responsible for the protection of your equipment and backup of your data.

Workflow Informatics will not be liable for any damages you may suffer in connection with using or modifying this SOFTWARE PRODUCT
______________________________________________________________________________________________________________________________________________

This python library encompasses all of the API function calls provided by CDD Vault.

If you're stuck, check out the Quickstart Guide


'''

import base64
import datetime as dt
import json
import numpy as np
import os
import pandas as pd
import requests
import sys
import time


class VaultClient(object):

    def __init__(self, vaultNum, apiKey):

        self.setVaultNumAndURL(vaultNum)
        self.setAPIKey(apiKey)

        self.setMaxSyncObjects()


    def __str__(self):

        return f'Client for Vault ID: {self.vaultNum} instantiated {str(dt.datetime.now())}'


    def setVaultNumAndURL(self, vaultNum):

        self.vaultNum = vaultNum

        URL = "https://app.collaborativedrug.com/api/v1/vaults/"
        URL = URL + str(vaultNum)

        self.URL = URL

        return (self.vaultNum, self.URL)


    def getVaultNum(self):

        return self.vaultNum
    

    def getURL(self):

        return self.URL


    def setAPIKey(self, apiKey):

        self.apiKey = apiKey


    def getAPIKey(self):

        return self.apiKey


    def setMaxSyncObjects(self, value=1000):
        """
        :Description: sets the 'maxSyncObjects' attribute, which is used to determine
                      when a synchronous vs asynchronous export request is submitted
                      to CDD. If the # of objects returned from a GET request is ever
                      >= maxSyncObjects, the call will be repeated asynchronously.

                      Defaults to 1000, the maximum # of objects which a CDD GET request
                      can return synhcronously.

                      Only used in methods where GET requests can be performed asynchronously:
                      Molecules, Batches, Plates, Protocols, and Protocol Data. See method
                      sendSyncAndAsyncGets().
        """

        self.maxSyncObjects = value

        return self.maxSyncObjects

    
    """
    GET Methods to Implement:

    ELN Entries -
    Molecule - finish adding help documentation for query parameters.
    Plot -
    Saved Search -

    POST Methods to Implement:

    ELN Entries -

    PUT Methods to Implement: done.

    DELETE Methods to Implement: done.
    
    """

    def formatHelp(self, valid_kwargs):
        """
        :Description: displays a help string describing the usage
                      for a particular set of query parameters, for
                      quick reference from Python.
        """

        helpString = ""

        for prm in valid_kwargs: 
            
            helpString += f"\n\n\n{prm}:\n\n{valid_kwargs[prm]}"

        print(helpString)
        return None


    def buildQueryString(self, kwargs, valid_kwargs):
        """
        :Description: Constructs the query string, which will be appended
                      to the URL endpoint when making GET requets.

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


    def sendGetRequest(self, URL, asText=False):

        headers = {"X-CDD-Token": self.apiKey}
        response = requests.get(URL, headers=headers)

        if asText and response.status_code == 200:

            return response.text

        # Check for errors:
        assert (response.status_code == 200), response.json()

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

            if objects["status"] == "canceled": 
                
                sys.exit(1)

        else: objects = objects["objects"]

        return objects


    def getAsyncExport(self, exportID, interval=5.0, asText=False, statusUpdates=True):
        """
        :Description: used to both check the status of an in-progress CDD asynchronous export,
                      as well as retrieve the data once the export has been completed.

                      Example output: 
                      
                      {'id': 19211628, 'created_at': '2022-11-03T02:02:12.000Z', 
                                        'modified_at': '2022-11-03T02:02:12.000Z', 'status': 'started'}

        :asText: determines whether the data in response is returned as a json (default behavior) or a string.

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

        response = self.sendGetRequest(URL)["objects"]
        return response


    def getBatches(self, asDataFrame=True, help=False, **kwargs):
        """
        :Description: return a collection of batches from CDD vault. 
        
        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-
        """

        # Construct URL:

        valid_kwargs = {"batches": 
                                    "Comma-separated list of ids.\n"
                                    "Cannot be used with other parameters",

                        "async": "Boolean. If true, do an asynchronous export (see Async Export).\n"
                                 "Use for large data sets. Note - always set to True when using Python API",

                        "no_structures": "Boolean. If true, omit structure representations\n" 
                                         "for a smaller and faster response. Default: false",

                        "only_ids": "Boolean. If true, only the Batch IDs are returned,\n" 
                                    "allowing for a smaller and faster response. Default: false",

                        "created_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
                        "created_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
                        "modified_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
                        "modified_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
                        "molecule_created_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
                        "molecule_created_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",

                        "page_size": "The maximum # of objects to return.",

                        "projects": "Comma-separated list of project ids.\n"
                                    "Defaults to all available projects.\n"
                                    "Limits scope of query.",
                        
                        #"data_sets",
                        "molecule_batch_identifier": "A Molecule-Batch ID used to query the Vault.\n" 
                                                     "Use this parameter to limit the number of Molecule UDF Fields to return",

                        "molecule_fields": "Array of Molecule field names to include in the resulting JSON.\n"
                                           "Use this parameter to limit the number of Molecule UDF Fields to return.",

                        "batch_fields": "Array of Batch field names to include in the resulting JSON.\n"
                                        "Use this parameter to limit the number of Batch UDF Fields to return.",

                        "fields_search": "Array of Batch field names & values. Used to filter Batches returned based on query values"}


        if help: return self.formatHelp(valid_kwargs)

        # Get batches + format output:

        suffix = "/batches"

        batches = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

        if asDataFrame: batches = pd.DataFrame.from_dict(batches)

        return batches


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


    def getFields(self, asDataFrame=True):
        """
        :Description: returns a list of available fields for the given vault.

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
        :Description: retrieves a single file object from CDD Vault using its file ID.

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


    def getMappingTemplates(self, id=None, asDataFrame=True):
        """
        :Description: returns summary information on all available mapping templates in the Vault specified.

                      Alternatively, if 'id' argument is set, will retrieve details on the data objects mapped 
                      within a specific mapping template.

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


    def getMolecules(self, asDataFrame=True, help=False, **kwargs):
        """
        :Description: return a list of molecules and their batches, based on optional parameters.
        
        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-
        """

        # Construct URL:

        valid_kwargs = {"molecules": 
                                    "Comma-separated list of ids (not molecule names!).\n"
                                    "Cannot be used with other parameters",

                        "names": "Comma-separated list of names/synonyms.",

                        "async": "Boolean. If true, do an asynchronous export (see Async Export).\n"
                                 "Use for large data sets. Note - always set to True when using Python API",

                        "no_structures": "Boolean. If true, omit structure representations\n" 
                                         "for a smaller and faster response. Default: false",

                        "only_ids": "Boolean. If true, only the Molecule IDs are returned,\n" 
                                    "allowing for a smaller and faster response. Default: false",

                        "created_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
                        "created_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
                        "modified_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",
                        "modified_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm)",

                        "batch_created_before": "",
                        "batch_created_after": "",
                        "batch_field_before_name": "",
                        "batch_field_before_date": "",
                        "batch_field_after_name": "",
                        "batch_field_after_date": "",


                        "page_size": "The maximum # of objects to return.",

                        "projects": "Comma-separated list of project ids.\n"
                                    "Defaults to all available projects.\n"
                                    "Limits scope of query.",

                        #"data_sets",
                        "structure": "SMILES, cxsmiles or mol string for the query structure.\n"
                                     "Returns Molecules from the Vault that match the structure-based\n" 
                                     "query submitted via this API call.",

                        "structure_search_type": "Available options are: 'exact', 'similarity' or 'substructure'.\n"
                                                 "Default option is substructure.",

                        "structure_similarity_threshold": "A number between 0 and 1. Include this parameter only if the structure_search_type is 'similarity'.",

                        "inchikey": "A valid InchiKey. Use this parameter instead of the \"structure\" and\n" 
                                    "\"structure_search_type\" parameters.",

                        "molecule_fields": "Array of Molecule field names to include in the resulting JSON.\n"
                                           "Use this parameter to limit the number of Molecule UDF Fields to return.",

                        "batch_fields": "Array of Batch field names to include in the resulting JSON.\n"
                                        "Use this parameter to limit the number of Batch UDF Fields to return.",

                        "fields_search": "Array of Molecule field names & values. Used to filter Molecules returned based on query values"}


        if help: return self.formatHelp(valid_kwargs)

        # Get molecules + format output:

        suffix = "/molecules"

        molecules = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

        if asDataFrame: molecules = pd.DataFrame.from_dict(molecules)

        return molecules


    def getPlates(self, asDataFrame=True, help=False, **kwargs):
        """
        :Description: return a collection of plates from CDD vault. 
        
        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005739586-Plate-s-GET-DELETE-
        """

        # Construct URL:

        valid_kwargs = {"plates": "Comma-separated list of ids.",
                                    
                        "names": "Comma-delimited list of plate names.",

                        "locations": "Comma-delimited list of plate locations.",

                        "async": "Boolean. If true, do an asynchronous export (see Async Export).\n"
                                 "Use for large data sets. Note - always set to True when using Python API",

                        "page_size": "The maximum # of objects to return.",

                        "projects": "Comma-separated list of project ids.\n"
                                    "Defaults to all available projects.\n"
                                    "Limits scope of query."}
                        

        if help: return self.formatHelp(valid_kwargs)

        # Get plates + format output:

        suffix = "/plates"

        plates = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

        if asDataFrame: plates = pd.DataFrame.from_dict(plates)

        return plates


    def getPlot(self, batchID, protocolID, size="small", destFolder=None):
        """
        :Description:
        """

        assert size in ["small", "medium", "large"], "Not a valid value."

        suffix = f"/batches/{batchID}/protocols/{protocolID}/plot"

        URL = self.URL + suffix + f"?{size}"; print(URL)

        response = self.sendGetRequest(URL=URL)
        print(response)


    def getProtocols(self, asDataFrame=True, help=False, **kwargs):
        """
        :Description: returns a list of protocols based on criteria as specified by parameters:
        
        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685406-Protocol-s-GET-
        """

        # Construct URL:

        valid_kwargs = {"protocols": 
                                    "Comma-separated list of protocol ids.\n"
                                    "Cannot be used with other parameters",

                        "names": "Comma-separated list of protocol names.\n"
                                  "Cannot be used with other parameters.",

                        "async": "Boolean. If true, do an asynchronous export (see Async Export).\n"
                                 "Use for large data sets. Note - always set to True when using Python API",

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

                        #"data_sets",
                         
                        "slurp": "Specify the slurp_id of an import operation.\n"
                                 "Once an import has been committed, you can return\n" 
                                 "additional JSON results that will expose the Protocol\n" 
                                 "and Run(s) of data that were imported."}


        if help: return self.formatHelp(valid_kwargs)
            
        # Get protocols + format output:

        suffix = "/protocols"

        protocols = self.sendSyncAndAsyncGets(suffix, kwargs, valid_kwargs)

        if asDataFrame: protocols = pd.DataFrame.from_dict(protocols)

        return protocols


    def getProtocolData(self, id=None, asDataFrame=True, help=False, statusUpdates=True, **kwargs):
        """
        :Description: returns (a subset of) the readout data for a single protocol using its protocol ID.
                      'id' argument is required, unless 'help' is set to True.
        
        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685426-Protocol-Data-GET-
        """

        # Construct URL:

        valid_kwargs = {"async": "Boolean. If true, do an asynchronous export (see Async Export).\n"
                                 "Use for large data sets. Note - always set to True when using Python API",

                        "plates": "Comma-separated list of plate ids. Include only data for the specified plates.",

                        "molecules": "Comma-separated list of molecule ids. Include only data for the specified molecules.",

                        "runs_before": "Date (YYYY-MM-DDThh:mm:ss±hh:mm). Include only data for runs on or before the date",

                        "runs_after": "Date (YYYY-MM-DDThh:mm:ss±hh:mm). Include only data for runs on or after the date.",

                        "runs": "Comma-separated list of run ids for the given protocol. Include only data for runs listed.",

                        "page_size": "The maximum # of objects to return.",

                        "projects": "Comma-separated list of project ids.\n"
                                    "Defaults to all available projects.\n"
                                    "Limits scope of query.",

                        "format": "'csv' - generates a csv file which mimics the file generated when you choose the 'Export readouts' button\n" 
                                  "from the Run-level 'Run Details' tab within the CDD Vault web interface.\n"

                                  "When used as a keyword argument, this forces an asynchronous GET request. All other keyword arguments will\n"
                                  "be ignored, excluding the 'runs' keyword if included."}


        if help: return self.formatHelp(valid_kwargs)

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


    def getRun(self, runID):
        """
        :Description: retrieve a single run using its unique run ID.
        
        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/360024315171-Run-s-GET-PUT-DELETE- 
        """

        suffix = f"/runs/{runID}"
        URL = self.URL + suffix

        run = self.sendGetRequest(URL)

        return run


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

        # Check for errors:
        assert (response.status_code == 200), response.json()
        
        return response.json()


    def postBatches(self, data=None, help=False):
        """
        :Description: creates a new batch in CDD Vault.

        :data: required, unless 'help' is set to True. Must be either a valid json object,
               or a string file path to a valid json file.

        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-
        """

        # Construct URL:

        allowedJsonKeys = {"class": "Optional. If present, must be 'batch'.",

                           "molecule": "See create a molecule when creating new molecules in a vault at:\n\n"
                                       "https://support.collaborativedrug.com/hc/en-us/articles/115005685466#create",

                           "name": "String (required).",

                           "projects": "An array of project ids and/or names (Required).",

                           "batch_fields": "Each vault has its own settings on the minimum information required to create a new Batch.\n" 
                                           "For a Vault Administrator, see Settings > Vault > Batch Fields, to change which Batch fields are required.\n\n"

                                           "{<batch_field_name>: <batch_field_value>, ... }",

                           "salt_name": "A two-letter code or Salt vendor string as listed here: https://app.collaborativedrug.com/support/salts.\n"  
                                        "The salt is determined automatically when the salt is included in the molecular structure.",

                           "solvent_of_crystallization_name": "Name of the solvent.",

                           "stoichiometry": "{\n"
                                            "\t\"core_count\": <integer>,\n"
                                            "\t\"salt_count\": <integer>,\n"
                                            "\t\"solvent_of_crystallization_count\": <integer>\n"
                                            "}" }



        if help: return self.formatHelp(allowedJsonKeys)
    
        suffix = "/batches"
        URL = self.URL + suffix
        

        # Post batch to CDD Vault + get response:

        response = self.sendPostRequest(URL, data)

        return response


    def postFiles(self, objectType, objectID, fileName):
        """
        :Description: attaches a file to an object (Run, Molecule, Protocol or ELN entry).

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
        assert (response.status_code == 200), response.json()

        return response.json()
    

    def postMolecules(self, data=None, help=False):
        """
        :Description: registers a new molecule in CDD Vault.

        :data: required, unless 'help' is set to True. Must be either a valid json object,
               or a string file path to a valid json file.

        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-
        """

        # Construct URL:

        allowedJsonKeys = {"class": "Optional. If present, must be 'molecule'.",

                        "name": "String (required).",

                        "smiles": "Only one of these [smiles, csxmiles, molfile, structure] may be present.\n" 
                        "'structure' accepts SMILES strings or Molfiles as values.\n" 
                        "For molfiles, replace all new lines with \\n (JSON requirement)",

                        "cxsmiles": "See smiles entry.",

                        "molfile": "See smiles entry.",

                        "structure": "See smiles entry.",

                        "description": "String.",

                        "synonyms": "An array of strings.",

                        "udfs": "{<udf_name>: <udf_value>, ... }",

                        "projects": "An array of project ids and/or names (Required).",

                        "collections": "An array of project ids and/or names." }


        if help: return self.formatHelp(allowedJsonKeys)
    
        suffix = "/molecules"
        URL = self.URL + suffix
        

        # Post molecule to CDD Vault + get response:

        response = self.sendPostRequest(URL, data)

        return response
    

    def postSlurpsData(self, fileName, project, mappingTemplate=None, runs=None, interval=5.0):
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

                            :run_date: use YYYY-MM-DDThh:mm:ss:hh:mm. Default is today’s date.

                            :place: this field is called 'lab' within the CDD Vault web interface. No default value provided.

                            :person: default value is user's full name.

                            :conditions: no default value provided.

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
            
        jsonObj = json.dumps(jsonObj)


        # Send request to initiate bulk upload:

        suffix = "/slurps"
        URL = self.URL + suffix

        headers = {"X-CDD-Token": self.apiKey}

        response = requests.post(URL, headers=headers, files=files, data={"json": jsonObj})
        assert (response.status_code == 200), response.json()


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
        assert outputResponse.status_code == 200, outputResponse.json()

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

        # Check for errors:
        assert (response.status_code == 200), response.json()
        
        return response.json()


    def putBatches(self, id=None, data=None, help=False):
        """
        :Description: updates an existing batch. 

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

        if help: return self.postBatches(help=True) # help=True calls help from postBatches() method, since inputs are the same.
    
        suffix = f"/batches/{id}"
        URL = self.URL + suffix
        

        # Put batch to CDD Vault + get response:

        response = self.sendPutRequest(URL, data)

        return response   


    def putMolecules(self, id=None, data=None, help=False):
        """
        :Description: updates an existing molecule. Some keys behave differently when used with
                      putMolecules() vs. postMolecules(). Run with help=True for more details.

        :id (int or str): unique id for an existing molecule object in CDD Vault.
                          Required, unless 'help' is set to True.

        :data: Must be either a valid json object, or a string file path to a valid json file. 
               Fields not specified in the JSON are not changed. See postMolecules() method for valid fields.
               Required, unless 'help' is set to True. 

        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-#update
        """

        # Construct URL:

        allowedJsonKeys = {
                        "name": "If this field is supplied, the old name is automatically added as a synonym.\n" 
                                "To delete a molecule name, you must exclude it from the list of synonyms.\n"
                                "Names cannot be changed in registration vaults.",

                        "synonyms": "If supplied, the list of synonyms replaces the existing list.",

                        "udfs": "Only fields explicitly mentioned will be changed.\n" 
                                "A user-defined field can be removed by using the value null (no quotes)."
                        }


        if help: return self.formatHelp(allowedJsonKeys)
    
        suffix = f"/molecules/{id}"
        URL = self.URL + suffix
        

        # Put molecule to CDD Vault + get response:

        response = self.sendPutRequest(URL, data)

        return response   


    def putRuns(self, id=None, data=None, help=False):
        """
        :Description: updates an existing run. 

        :id (int or str): unique id for an existing run object in CDD Vault.
                          Required, unless 'help' is set to True.

        :data: Must be either a valid json object, or a string file path to a valid json file. 

               Fields not specified in the JSON are not changed. Allows users to update the run Project association 
               and the Run_Date, Person, Place, and Conditions fields. Required, unless 'help' is set to True. 

        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/360024315171-Run-s-GET-PUT-DELETE-#update
        """

        # Construct URL:

        if help: 
            
            print("No additional help defined.")
            return 
    
        suffix = f"/runs/{id}"
        URL = self.URL + suffix
        

        # Put run to CDD Vault + get response:

        response = self.sendPutRequest(URL, data)

        return response   
 

    def putReadoutRows(self, id=None, data=None, help=False):
        """
        :Description: updates an existing readout row (including the ability to flag an existing readout row as an outlier).

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

        if help: 
            
            print("No additional help defined.")
            return 
    
        suffix = f"/readout_rows/{id}"
        URL = self.URL + suffix
        

        # Put readout row to CDD Vault + get response:

        response = self.sendPutRequest(URL, data)

        return response   
    

    def sendDeleteRequest(self, URL):

        headers = {"X-CDD-Token": self.apiKey}
        response = requests.delete(URL, headers=headers)

        # Check for errors:
        assert (response.status_code == 200), response.json()
        
        return response.json()


    def deleteFiles(self, fileID):
        """
        :Description: deletes a single file attached to an object (Run, Molecule, Protocol or ELN entry)
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


    def deleteBatches(self, id):
        """
        :Description: deletes a batch present in CDD Vault.

                      Note that for safety/security purposes, batches which have data associated with them cannot be deleted 
                      via this method call. Data (such as rows of readout data in a Protocol Run) must be removed prior to using 
                      this method call to delete a Batch.
        
        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005682943-Batch-es-GET-POST-PUT-#update
        """

        # Note that batch deletes are actually performed using PUT requests, which must be submitted with an empty
        # projects array for the specified batch id.

        return self.putBatches(id, data={"projects": []})


    def deleteExport(self, id):
        """
        :Description: deletes an in-progress asynchronous export.

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


    def deleteMolecules(self, id):
        """
        :Description: deletes a molecule present in CDD Vault.
        
        :Reference: https://support.collaborativedrug.com/hc/en-us/articles/115005685466-Molecule-s-GET-POST-PUT-#update
        """

        # Note that molecule deletes are actually performed using PUT requests, which must be submitted with an empty
        # projects array for the specified molecule id.

        return self.putMolecules(id, data={"projects": []})


    def deletePlates(self, id):
        """
        :Description: deletes a single existing plate in CDD Vault using its plate ID.

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
        :Description: deletes a single readout row associated with protocol data in CDD Vault using its unique ID.

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
        :Description: either deletes a single run from CDD vault or deletes all runs associated with a 
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

