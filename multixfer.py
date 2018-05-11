import datetime
import argparse
import json
import jsonschema
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import signal
import time

multixfer_schema = {
  "title":"multixfer schema",
  "type": "object",
  "properties": {
    "inputVersion": {
      "type":"number",
      "minumum":1.0,
      "maximum":1.1
    },
    "testName": {
      "type":"string"
    },
    "repeat": {
      "description":"Number of times to loop thru the targets; 0 is infinite; 0 is default",
      "type": "integer",
      "minimum":0
    },
    "pauseFreq" : {
        "description":"Pause every this many loops. 0 is never; otherwise every mod loop count; e.g. 8 is every 8th time",
        "type": "integer",
        "minimum":0,
        "default":0
    },
    "pause" : {
        "description":"Pause this many seconds every pauseFreq",
        "type": "integer",
        "minimum":0,
        "default":0
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
            "description":"get or put operation; get is default",
            "type": "string"
          }
        },
        "required":["url"]
      }
    }
  },
  "required":["inputVersion","testName","repeat","targets"]
}

class TestTarget:
    def __init__(self, jsonDef):
        self.url = jsonDef["url"]
        try:
            self.operation = jsonDef["operation"]
        except:
            self.operation = "get"

        self.successfulCount = 0
        self.failedCount = 0
        self.bytesTransfered = 0

    def __str__(self):
        return str(self.__dict__)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)

class TestDefinition:
    def __init__(self, jsonDef):
        self.result = 'failed'
        self.inputVersion = jsonDef["inputVersion"]
        self.verifyCert = jsonDef["verifyCert"]
        self.repeat = jsonDef["repeat"]
        self.testName = jsonDef["testName"]
        self.targets = []
        self.successfulCount = 0
        self.failedCount = 0
        self.bytesTransfered = 0
        self.inputFilename = ''
        try:
           self.pauseFreq = jsonDef["pauseFreq"]
           self.pause = jsonDef["pause"]
        except:
            self.pauseFreq = 0
            self.pause = 0

        for iTarget in range(len(jsonDef["targets"])):
            target = TestTarget(jsonDef["targets"][iTarget])
            self.targets.append(target)

    def __str__(self):
        return str(self.__dict__)

    def dropResults(self, outputFilename=''):
        if(len(outputFilename)==0):
            outputFilename = self.inputFilename + '_results_' + time.strftime("%Y%m%d%H%M%SZ", time.gmtime())
        outFile = open(outputFilename, 'w')
        outFile.write(self.toJSON())
        outFile.close()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)

    def failedExit(self, reason='failed'):
        print('Exiting: ' + reason);
        self.result = reason
        self.Exit()

    def successfulExit(self):
        self.result = 'successful'
        self.Exit()

    def Exit(self):
        print(testDef.toJSON())
        testDef.dropResults()
        exit()

# Starts running here

argParser = argparse.ArgumentParser("Perform multiple gets/puts requests")
argParser.add_argument('--inputFile', dest='inputFile', help='test definition JSON input file')
args = argParser.parse_args()
print('Using Input file:' + args.inputFile)

# Read the input file into json
with open(args.inputFile) as json_data:
    testDefJson = json.load(json_data)
    jsonschema.validate(testDefJson, multixfer_schema)        

    testDef = TestDefinition(testDefJson)
    testDef.inputFilename = args.inputFile

def signal_handler(signal, frame):
    userReason = 'User Terminated'
    testDef.failedExit(userReason)

# start iterations

signal.signal(signal.SIGINT, signal_handler)

forever = False
if (testDef.repeat == 0):
   forever = True

repeatCount = 0

while(forever or repeatCount < testDef.repeat):
   repeatCount += 1
   print('Iteration: ' + str(repeatCount))


   for target in testDef.targets:
       if(target.operation == 'get'):
          print('\tget: ' + target.url)
          try:
             req = requests.get(target.url, verify=testDef.verifyCert)
          except:
             target.failedCount += 1
             testDef.failedExit()

          contentLen = int(req.headers['Content-Length'])
          target.bytesTransfered += contentLen
          testDef.bytesTransfered += contentLen
          mbpsec = contentLen / 1024 / 1024 / req.elapsed.total_seconds()
          print('test')
          print('\t\t' + str(contentLen) + ' bytes downloaded in ' + str(req.elapsed.total_seconds()) + 'sec, ' + "{0:.2f}".format(mbpsec) + ' MB/sec')
       elif(target.operation == 'put'):
          print('Put not supported')

       if(req.status_code != 200):
         target.failedCount += 1
         testDef.failedCount += 1
         print('Target failed: ' + target.url)
         testDef.failedExit()
       else:
         target.successfulCount += 1
         testDef.successfulCount += 1

   print('Bytes transfered so far: ' + str(testDef.bytesTransfered))
   
   if(testDef.pause > 0 and testDef.pauseFreq > 0 and repeatCount % testDef.pauseFreq == 0):
       print('...Sleeping ' + str(testDef.pause) + 'sec...')
       time.sleep(testDef.pause)

testDef.successfulExit()