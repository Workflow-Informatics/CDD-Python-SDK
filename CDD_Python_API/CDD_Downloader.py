
import json
import os
import pandas as pd
import shutil
import sys

from CDD_API_Client import VaultClient


class CDD_Downloader(VaultClient):

    def __init__(self, vaultNum, apiKey, topDir):

        super().__init__(vaultNum, apiKey)

        self.setTopDir(topDir)

        self.setAvailableProjects()
        self.setProjects(self.availableProjects["name"])

        self.setAvailableProtocols()
        self.setProtocols(self.availableProtocols["name"])

        self.setRunDates()


    def setTopDir(self, topDir):

        topDir = os.path.join(topDir, 
                              f"Vault_{self.vaultNum}")

        self.topDir = topDir
        return self.topDir


    def setAvailableProjects(self):

        self.availableProjects = self.getProjects()

        return self.availableProjects


    def setAvailableProtocols(self):

        self.availableProtocols = self.getProtocols()
        self.availableProtocols = self.availableProtocols[["name", "id"]]

        return self.availableProtocols


    def filterDataFrameRows(self, df, names, IDs):

        if names is not None:

            df = df[df["name"].isin(names)]

        elif IDs is not None:

            df = df[df["id"].isin(IDs)]

        df = df.set_index('id').T.to_dict('list')
        df = {k:v[0] for k,v in df.items()}

        return df


    def setProjects(self, names=None, IDs=None):

        projects = self.availableProjects
        self.projects = self.filterDataFrameRows(df=projects,
                                                 names=names,
                                                 IDs=IDs)

        return self.projects


    def setProtocols(self, names=None, IDs=None):

        protocols = self.availableProtocols
        self.protocols = self.filterDataFrameRows(df=protocols,
                                                  names=names,
                                                  IDs=IDs)

        return self.protocols


    def setRunDates(self, runs_before=None, runs_after=None):

        self.runs_before = runs_before
        self.runs_after = runs_after

        return (self.runs_before, self.runs_after)


    def downloadCDDRuns(self):


        def locateCDDRuns():

            # Retrieve CDD runs belonging to the protocol ID's specified
            # in the 'protocols' attribute as a DataFrame.

            runs = []

            protoIDs = [str(k) for k in self.protocols.keys()]
            protoIDs = ",".join(protoIDs)

            protoInfo = self.getProtocols(protocols=protoIDs, asDataFrame=False)
            protoInfo = [p for p in protoInfo if "runs" in p]

            for p in protoInfo:

                protoID = p["id"]
                protoName = p["name"]

                for r in p["runs"]:

                    runID = r["id"]
                    runDate = r["run_date"]
                    runModDate = r["modified_at"]

                    projID = r["project"]["id"]
                    projName = r["project"]["name"]

                    runs.append([projID, projName,
                                protoID, protoName,
                                runID, runDate, runModDate])

            runs = pd.DataFrame(runs, columns=[
                                            "Project ID", "Project Name",
                                            "Protocol ID", "Protocol Name",
                                            "Run ID", "Run Date", "Run Modified Date"
                                            ])

            return runs


        def filterCDDRuns(runs):

            # Removes CDD runs outside the list of Project ID's in the 'projects' attribute
            # or which have runs > 'runs_before', runs < 'runs_after' attributes.

            runs = runs.sort_values(by=["Project ID", "Protocol ID", "Run Date"])

            runs = runs[runs["Project ID"].isin(self.projects.keys())].reset_index(drop=True)

            if self.runs_before: 
                
                runs = runs[runs["Run Date"] <= self.runs_before].reset_index(drop=True)

            if self.runs_after:

                runs = runs[runs["Run Date"] >= self.runs_after].reset_index(drop=True)

            return runs.astype(str)


        def buildTargetPaths(runs):

            # Appends a column to runs DataFrame, specifying the destination folders where
            # run data + metadata should be written to.

            runs["Proj_SubDir"] = runs["Project Name"] + "_" + runs["Project ID"]
            runs["Proto_SubDir"] = runs["Protocol Name"] + "_" + runs["Protocol ID"]
            runs["Run_SubDir"] = runs["Run Date"] + "_" + runs["Run ID"]

            runs["Target Folder"] = runs[["Proj_SubDir", "Proto_SubDir", "Run_SubDir"]].apply(
                                        lambda row: os.path.join(self.topDir, *row), axis=1)

            runs = runs[['Project ID', 'Project Name', 
                         'Protocol ID', 'Protocol Name', 
                         'Run ID', 'Run Date', 'Run Modified Date', 
                         'Target Folder']]

            return runs


        def extractCDDRuns(runs):

            # Extract specified runs from CDD Vault to a subfolder under 'topDir' attribute.

            for r in runs.iterrows():

                r = r[1]

                runID = r["Run ID"]
                protoID = r["Protocol ID"]
                cddRunModDate = r["Run Modified Date"] # Up-to-date run modified date from CDD.

                targetFolder = r["Target Folder"]
                if not os.path.exists(targetFolder): os.makedirs(targetFolder)

                dataFile = os.path.join(targetFolder, f"run-data-{runID}.csv")
                metaFile = os.path.join(targetFolder, f"run-meta-{runID}.json")

                # Skip run download if modified date has not changed since prev extraction:

                if os.path.exists(dataFile) and os.path.exists(metaFile):

                    localRunModDate = json.load(fp=open(metaFile))["modified_at"]
                    if localRunModDate == cddRunModDate: continue

                data = self.getProtocolData(id=protoID, format="csv", runs=runID, statusUpdates=False)
                meta = self.getRun(runID=runID)

                print(data, file=open(dataFile, "w"))
                json.dump(meta, indent=4, fp=open(metaFile, "w"))
                print(f"Extracted run '{runID}' to path:\n{dataFile}\n")

            return runs


        def removeExtraRunDirs(runs):

            # Check if any local run subdirectories no longer exist in CDD + optionally delete:

            pathsToDelete = []

            localRunDirs = [p[0] for p in os.walk(self.topDir) if len(p[1]) == 0]
            localRunIDs = [p.split("_")[-1] for p in localRunDirs]

            for i in range(len(localRunIDs)):

                ID = localRunIDs[i]
                if ID not in runs["Run ID"].values: pathsToDelete.append(localRunDirs[i])

            endLine = "\n"
            deletePaths = input("\nDelete the following local paths (y/n):"
                                f"\n\n{endLine.join(pathsToDelete)}\n\n")

            if deletePaths[0].lower() == "y": 
                
                for p in pathsToDelete:

                    print(f"Deleting run folder '{p}'")
                    shutil.rmtree(p)

            return runs


        runs = locateCDDRuns()
        runs = filterCDDRuns(runs)
        runs = buildTargetPaths(runs)
        runs = extractCDDRuns(runs)
        runs = removeExtraRunDirs(runs)

