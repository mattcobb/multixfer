multixfer.py --help

usage: Perform multiple gets/puts requests [-h] [--inputFile INPUTFILE]

optional arguments:
  -h, --help              show this help message and exit
  --inputFile INPUTFILE   test definition JSON input file

Input file example:
```json
{
   "inputVersion":1.0,
   "testName":"Download test object",
   "repeat":2,
   "verifyCert":false,
   "targets":[
      {
         "url":"https://jenkins.cobbsweb.us/job/A/lastSuccessfulBuild/artifact/OUTPUT/Release/Installer_2.2.0.exe",
         "operation":"get"
      },
      {
         "url":"https://jenkins.cobbsweb.us/job/B/lastSuccessfulBuild/artifact/OUTPUT/Release/Installer_2.2.0.exe",
         "operation":"get"
      }
   ]
}
```

Example run:

multixfer.py --inputFile=inputs\nightlytest.json

Example resutls:
```json
{
  "result": "failed",
  "inputVersion": 1.0,
  "verifyCert": false,
  "repeat": 2,
  "testName": "Download test object",
  "targets": [
    {
      "url": "https://jenkins.cobbsweb.us/job/A/lastSuccessfulBuild/artifact/OUTPUT/Release/Installer_2.2.0.exe",
      "operation": "get",
      "successfulCount": 0,
      "failedCount": 1,
      "bytesTransfered": 0
    },
    {
      "url": "https://jenkins.cobbsweb.us/job/B/lastSuccessfulBuild/artifact/OUTPUT/Release/Installer_2.2.0.exe",
      "operation": "get",
      "successfulCount": 1,
      "failedCount": 0,
      "bytesTransfered": 1000
    }
  ],
  "successfulCount": 1,
  "failedCount": 1,
  "bytesTransfered": 1000,
  "inputFilename": "inputs\\nightlytest.json"
}
```

Input file schema:
```json
{
  "title":"multixfer schema",
  "type": "object",
  "properties": {
    "inputVersion": {
      "type":"number",
      "minumum":1.0,
      "maximum":1.0
    },
    "testName": {
      "type":"string"
    },
    "repeat": {
      "description":"Number of times to loop thru the targets; 0 is infinite; 0 is default",
      "type": "integer",
      "minimum":0
    },
    "verifyCert": {
      "type": "boolean"
    },
    "targets": {
      "type": "array",
      "items": {
        "type":"object",
        "properties": {
          "url": {
            "type":"string"
          },
          "operation": {
            "description":"get or put operation",
            "type": "string"
          }
        }
      }
    }
  }
}
```
