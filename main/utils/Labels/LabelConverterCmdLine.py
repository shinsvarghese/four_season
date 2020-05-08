import argparse
import pickle
from Label.Config import mongoDBConfig
from Label.DataMapping import DataBaseDataMapper

def displayMessage(displayString):
    print (displayString)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='Name Of the data base')

    try:
        arguments = parser.parse_args()
        if arguments.path:
            with open(arguments.path, 'r') as fileObject:
                config = pickle.load(fileObject)
                DataBaseDataMapperI = DataBaseDataMapper()
                if DataBaseDataMapperI.performMongoDBConnection(config.uri, config.db, config.coll):
                    retVal = DataBaseDataMapperI.extractLabels(str(config.sqlPath), config.countryList,
                                                               config.signList)
                    if not retVal:
                        displayMessage("Mapped Sequence is not present")
                else:
                    displayMessage( "Could not connect to MongoDB")

        else:
            displayMessage( "Provide the pickle file path")

    except SystemExit:
        displayMessage( "unable to parse command line arguments")