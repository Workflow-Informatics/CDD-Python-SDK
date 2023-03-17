# CDD-Python-API

## A Python client for rapid execution of [CDD Vault API methods](https://support.collaborativedrug.com/hc/en-us/sections/115001607043-API-Function-Calls).

### Installation

To install, run:

```bash
git clone https://github.com/Workflow-Informatics/CDD-Python-API.git
cd CDD-Python-API/
python setup.py install
```

### Getting Started

Instantiate a client for working with your vault data:
```python
from cdd.VaultClient import VaultClient

vaultNum = 4598 # Insert your unique vault ID here.
apiToken = os.environ["cddAPIToken"] # Insert your API token here.

vault = VaultClient(vaultNum, apiToken)
```

__GET Methods to Implement:__

  - Molecules: finish adding help documentation for query parameters.
  - Plot: TBD
  - Saved Search: TBD

__POST Methods to Implement: done.__

__PUT Methods to Implement: done.__

__DELETE Methods to Implement: done.__

__QOL Changes__:

 - Set dataframe indexes based on responses 
