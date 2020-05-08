__author__ = 'uidq1602'

import sys

class SqlStringHelper:

    def __init__(self):
        self.__CountryListStringPVS = "select COUNTRY from L_FRAME_PVS group by COUNTRY"
        self.__CountryListString = "select COUNTRY from L_FRAME group by COUNTRY"

        self.__SignListPVS = "select SIGN_CLASS from L_SIGN_PVS group by SIGN_CLASS"
        self.__SignList = "select SIGN_CLASS from L_SIGN group by SIGN_CLASS"

        self.__SequenceListPVS = "select SEQUENCE from L_FRAME_PVS  where COUNTRY = (\"%s\") group by SEQUENCE"
        self.__SequenceList = "select SEQUENCE from L_FRAME where COUNTRY = (\"%s\") group by SEQUENCE"

        self.__SensorList = "select SENSOR_PLATFORM from L_STATIC group by SENSOR_PLATFORM"

        self.__checkSequenceStringPVS = "select SIGN_CLASS from L_SIGN_PVS where SEQUENCE = \"%s\" group by SIGN_CLASS"
        self.__checkSequenceString = "select SIGN_CLASS from L_SIGN where SEQUENCE = \"%s\" group by SIGN_CLASS"

        self.__pathStringPVS = "select PATH from L_SEQUENCES_PVS where SEQUENCE = \"%s\""
        self.__pathString = "select PATH from L_SEQUENCE where SEQUENCE = \"%s\""

        self.__signIDStringPVS = "select * from L_SIGN_PVS where SEQUENCE = \"%s\" and SIGN_CLASS = \"%s\" group by SIGN_ID"
        self.__signIDString = "select * from L_SIGN where SEQUENCE = \"%s\" and SIGN_CLASS = \"%s\" group by SIGN_ID"

        self.__signDataStringPVS = "select * from L_SIGN_PVS where SEQUENCE = \"%s\" and SIGN_CLASS = \"%s\" and SIGN_ID = \"%s\""
        # self.__signDataString = "select * from L_SIGN where SEQUENCE = \"%s\"  and SIGN_ID = \"%s\""
        # self.__signDataString = "select * from L_SIGN where SEQUENCE = \"%s\" and SIGN_CLASS = \"%s\" and SIGN_ID = \"%s\""
        self.__signDataString = "select * from L_SIGN cross join L_STATIC using(SEQUENCE) where SEQUENCE = \"%s\"  and SIGN_ID = \"%s\""
        # self.__signDataStringPVS = "select * from L_SIGN_PVS inner Join L_STATIC_PVS using (sequence)  where SEQUENCE = \"%s\" and SIGN_CLASS = \"%s\" and SIGN_ID = \"%s\""

        self.__ROIAndFrameInfoStringPVS = "select * from L_ROI_PVS cross join L_FRAME_PVS  using (SEQUENCE, TIMESTAMP) where SEQUENCE = \"%s\" and SIGN_ID in (%s) and COUNTRY =\"%s\""
        # self.__ROIAndFrameInfoString = "select * from L_ROI cross join L_FRAME using (SEQUENCE) where SEQUENCE = \"%s\" and SIGN_ID in (%s) and COUNTRY =\"%s\""
        # self.__ROIAndFrameInfoString = "select * from L_ROI cross join (select SEQUENCE,COUNTRY,ROAD_TYPE,ROAD_WORKS,WEATHER,STREET_CONDITIONS,LIGHT_CONDITIONS,CONTAMINATION,TUNNEL from L_FRAME)  using (SEQUENCE) where SEQUENCE = \"%s\" " \
        #                                "and SIGN_ID in (%s) and COUNTRY =\"%s\" "
        # self.__ROIAndFrameInfoString = "select * from L_ROI cross join L_FRAME using (SEQUENCE, TIMESTAMP) where SEQUENCE = \"%s\" and SIGN_ID in (%s) and COUNTRY =\"%s\""
        self.__ROIAndFrameInfoString = "select * from L_ROI cross join L_FRAME using (SEQUENCE, TIMESTAMP) where SEQUENCE = \"%s\"  and COUNTRY =\"%s\"" \
                                       "and TIMESTAMP in (select TIMESTAMP from L_ROI where SEQUENCE = \"%s\"  and SIGN_ID in  (%s) )"

        self.__LabelSourcePVS="select  LABEL_CHECKPOINT from L_CHECKPOINT_PVS"
        self.__LabelSource = "select  LABEL_CHECKPOINT from L_CHECKPOINT"
        self.__SensorType="select SENSOR_PLATFORM from L_STATIC where SEQUENCE=\"%s\" "


    def getCountryListString(self,signType):
        if signType=='PVS':
            return self.__CountryListStringPVS
        if signType=='mainSign':
            return self.__CountryListString

    def getSignListString(self,signType):
        if signType=='PVS':
            return self.__SignListPVS
        if signType=='mainSign':
           return self.__SignList

    def getSequenceList(self, CountryName,signType):
        if signType=='PVS':
            sequenceString = self.__SequenceListPVS % (CountryName)
        if signType=='mainSign':
            sequenceString = self.__SequenceList % (CountryName)

        return sequenceString

    def getSensorListString(self):
        return self.__SensorList

    def getCheckSequenceString(self, sequenceName,signType):
        if signType=='PVS':
          return self.__checkSequenceStringPVS % (sequenceName)
        elif signType=='mainSign':
            return self.__checkSequenceString % (sequenceName)

    def getPathString(self, sequenceName,signType):
        if signType=='PVS':
            return self.__pathStringPVS % (sequenceName)
        elif signType=='mainSign':
            return self.__pathString % (sequenceName)

    def getSignIDString(self, sequenceName, className,signType):
        if signType=='PVS':
            return self.__signIDStringPVS % (sequenceName, className)
        elif signType=='mainSign':
            return self.__signIDString % (sequenceName, className)
    def getSensorType(self,sequence):
        return self.__SensorType % (sequence)

    def getSignDataString(self,sequenceName, className, signID,signType):
        if signType=='PVS':
            return self.__signDataStringPVS % (sequenceName, className, signID)
        elif signType=='mainSign':
            # return self.__signDataString % (sequenceName, className, signID)
            return self.__signDataString % (sequenceName,signID)

    def convertToSignIdString(self, signId):
        finalSignIdString = ""
        if isinstance(signId, list):
            appendComma = False
            for oneSignId in signId:
                if appendComma == True:
                    finalSignIdString = finalSignIdString + ","

                finalSignIdString = finalSignIdString + str(oneSignId)
                appendComma = True
        else:
            finalSignIdString = str(signId)
        return finalSignIdString

    def getLabelSource(self,signType):
        if signType=='PVS':
             return  self.__LabelSourcePVS
        elif signType=='mainSign':
            return  self.__LabelSource

    def getROIAndFrameInfoString(self,sequenceName, signId, country,signType):
        if signType=='PVS':
            return  self.__ROIAndFrameInfoStringPVS % (sequenceName, self.convertToSignIdString(signId),country)
        elif signType=='mainSign':
             return self.__ROIAndFrameInfoString % (sequenceName,country,sequenceName,self.convertToSignIdString(signId))
