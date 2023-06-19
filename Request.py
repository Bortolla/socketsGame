class Request:
    def __init__(self, requestCode=None, address=None, connection=None, token=None, requestData={}) -> None:
        self.requestCode = requestCode
        self.token = token
        self.address = address
        self.connection = connection
        self.requestData = requestData
    
    def getRequestCode(self):
        return self.requestCode
    
    def getToken(self):
        return self.token
    
    def getAddress(self):
        return self.address
    
    def getRequestData(self):
        return self.requestData

    def getConnection(self):
        return self.connection

    def createRequestFromArray(self, array):
        if 'requestCode' in array:
            requestCode = array['requestCode']
        else:
            requestCode = None
        if 'token' in array:
            token = array['token']
        else:
            token = None
        if 'requestData' in array:
            requestData = array['requestData']
        else:
            requestData = None
        if 'address' in array:
            address = array['address']
        else:
            address = None
        if 'connection' in array:
            connection = array['connection']
        else:
            connection = None
        
        return Request(requestCode=requestCode, address=address, connection=connection, token=token, requestData=requestData)

    def getRequestAsArray(self):
        returnData = {
            'requestCode': self.requestCode,
            'token': self.token,
            'connection': self.connection,
            'requestData': self.requestData
        }

        return returnData
