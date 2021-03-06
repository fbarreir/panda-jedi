import sys
try:
    metaID = sys.argv[1]
except:
    metaID = None
import json
import uuid
taskParamMap = {}
taskParamMap['taskName'] = str(uuid.uuid4())
taskParamMap['userName'] = 'pandasrv1'
taskParamMap['vo'] = 'atlas'
taskParamMap['taskPriority'] = 100
taskParamMap['architecture'] = 'i686-slc5-gcc43-opt'
taskParamMap['transUses'] = 'Atlas-17.2.7'
taskParamMap['transHome'] = 'AtlasProduction-17.2.8.10'
taskParamMap['transPath'] = 'Reco_trf.py'
taskParamMap['processingType'] = 'reco'
taskParamMap['prodSourceLabel'] = 'test'
taskParamMap['taskType'] = 'prod'
taskParamMap['workingGroup'] = 'AP_Higgs'
taskParamMap['coreCount'] = 1
taskParamMap['cloud'] = 'US'
logDatasetName = 'panda.jeditest.log.{0}'.format(uuid.uuid4())
taskParamMap['log'] = {'dataset': logDatasetName,
                       'type':'template',
                       'param_type':'log',
                       'token':'ATLASDATADISK',
                       'value':'{0}.${{SN}}.log.tgz'.format(logDatasetName)}
outDatasetName = 'panda.jeditest.NTUP_EMBLLDN.{0}'.format(uuid.uuid4())
taskParamMap['jobParameters'] = [
    {'type':'template',
     'param_type':'input',
     'value':'inputAODFile=${IN}',
     'dataset':'data12_8TeV.00214651.physics_Egamma.merge.AOD.f489_m1261',
     },
    {'type':'constant',
     'value': 'maxEvents=1000 RunNumber=213816 autoConfiguration=everything preExec="from BTagging.BTaggingFlags import BTaggingFlags;BTaggingFlags.CalibrationTag=\"BTagCalibALL-07-02\""'
     },
    {'type':'template',
     'param_type':'input',
     'value':'DBRelease=${DBR}',
     'dataset':'ddo.000001.Atlas.Ideal.DBRelease.v220701',
     'attributes':'repeat,nosplit',
     },
    {'type':'constant',    
     'value':'AMITag=p1462'
     },
    {'type':'template',
     'param_type':'output',
     'token':'ATLASDATADISK',     
     'value':'outputNTUP_EMBLLDNFile={0}.${{SN}}.pool.root'.format(outDatasetName),
     'dataset':outDatasetName,
     }
    ]

jonStr = json.dumps(taskParamMap)

from pandajedi.jedicore.JediTaskBufferInterface import JediTaskBufferInterface

tbIF = JediTaskBufferInterface()
tbIF.setupInterface()
tbIF.insertTaskParams_JEDI(taskParamMap['vo'],taskParamMap['prodSourceLabel'],taskParamMap['userName'],taskParamMap['taskName'],jonStr)

