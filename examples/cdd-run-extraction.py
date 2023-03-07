
import os
import sys

cddLibPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "src")
sys.path.append(cddLibPath)

from CDD_Downloader import CDD_Downloader

if __name__ == "__main__":

    vaultNum = 4598
    topDir = os.getcwd()
    apiKey = os.environ["cddAPIToken"]

    args = [vaultNum, apiKey, topDir]

    cddDownloader = CDD_Downloader(*args)

    projNames = ["BioUDM", "My Special Project"]

    cddDownloader.setProjects(projNames)

    cddDownloader.setRunDates(runs_before="2022-10-17", 
                              runs_after="2022-05-15")

    cddDownloader.downloadCDDRuns()