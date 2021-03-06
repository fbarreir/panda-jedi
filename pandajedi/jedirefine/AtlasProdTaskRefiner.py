import re
import sys

from pandajedi.jedicore import Interaction
from TaskRefinerBase import TaskRefinerBase

from pandaserver.dataservice import DataServiceUtils


# brokerage for ATLAS production
class AtlasProdTaskRefiner (TaskRefinerBase):

    # constructor
    def __init__(self,taskBufferIF,ddmIF):
        TaskRefinerBase.__init__(self,taskBufferIF,ddmIF)



    # extract common parameters
    def extractCommon(self,jediTaskID,taskParamMap,workQueueMapper,splitRule):
        # set ddmBackEnd
        if not 'ddmBackEnd' in taskParamMap:
            taskParamMap['ddmBackEnd'] = 'rucio'
        TaskRefinerBase.extractCommon(self,jediTaskID,taskParamMap,workQueueMapper,splitRule)



    # main
    def doRefine(self,jediTaskID,taskParamMap):
        # make logger
        tmpLog = self.tmpLog
        tmpLog.debug('start taskType={0}'.format(self.taskSpec.taskType))
        try:
            self.doBasicRefine(taskParamMap)
            # set nosplit+repeat for DBR
            for datasetSpec in self.inSecDatasetSpecList:
                if DataServiceUtils.isDBR(datasetSpec.datasetName):
                    datasetSpec.attributes = 'repeat,nosplit'
            # enable consistency check
            if not self.taskSpec.parent_tid in [None,self.taskSpec.jediTaskID]:
                for datasetSpec in self.inMasterDatasetSpec:
                    if datasetSpec.isMaster() and datasetSpec.type == 'input':
                        datasetSpec.enableCheckConsistency()
            # append attempt number
            for tmpKey,tmpOutTemplateMapList in self.outputTemplateMap.iteritems():
                for tmpOutTemplateMap in tmpOutTemplateMapList:
                    outFileTemplate = tmpOutTemplateMap['filenameTemplate']
                    if re.search('\.\d+$',outFileTemplate) == None and not outFileTemplate.endswith('.panda.um'):
                        tmpOutTemplateMap['filenameTemplate'] = outFileTemplate + '.1'
            # extract datatype and set destination if nessesary
            datasetTypeList = []
            for datasetSpec in self.outDatasetSpecList:
                datasetType = DataServiceUtils.getDatasetType(datasetSpec.datasetName)
                if datasetType != '':
                    datasetTypeList.append(datasetType)
                storageToken = DataServiceUtils.getDestinationSE(datasetSpec.storageToken)
                if storageToken != None:
                    tmpSiteList = self.ddmIF.getInterface(self.taskSpec.vo).getSitesWithEndPoint(storageToken,self.siteMapper,'production')
                    if tmpSiteList == []:
                        raise RuntimeError,'cannot find online siteID associated to {0}'.format(storageToken)
                    datasetSpec.destination = tmpSiteList[0]
            # set numThrottled to use the task throttling mechanism
            if not 'noThrottle' in taskParamMap:
                self.taskSpec.numThrottled = 0
            # set to register datasets
            self.taskSpec.setToRegisterDatasets()
            # set transient to parent datasets
            if self.taskSpec.processingType in ['merge'] and not self.taskSpec.parent_tid in [None,self.taskSpec.jediTaskID]:
                # get parent
                tmpStat,parentTaskSpec = self.taskBufferIF.getTaskDatasetsWithID_JEDI(self.taskSpec.parent_tid,None,False)
                if tmpStat and parentTaskSpec != None:
                    # set transient to parent datasets
                    metaData = {'transient':True}
                    for datasetSpec in parentTaskSpec.datasetSpecList:
                        if datasetSpec.type in ['log','output']:
                            datasetType = DataServiceUtils.getDatasetType(datasetSpec.datasetName)
                            if datasetType != '' and datasetType in datasetTypeList:
                                tmpLog.info('set metadata={0} to parent jediTaskID={1}:datasetID={2}:Name={3}'.format(str(metaData),
                                                                                                                      self.taskSpec.parent_tid,
                                                                                                                      datasetSpec.datasetID,
                                                                                                                      datasetSpec.datasetName))
                                for metadataName,metadaValue in metaData.iteritems():
                                    self.ddmIF.getInterface(self.taskSpec.vo).setDatasetMetadata(datasetSpec.datasetName,
                                                                                                 metadataName,metadaValue)
        except:
            errtype,errvalue = sys.exc_info()[:2]
            tmpLog.error('doBasicRefine failed with {0}:{1}'.format(errtype.__name__,errvalue))
            raise errtype,errvalue
        tmpLog.debug('done')
        return self.SC_SUCCEEDED
            
    
