class Request:
    def __init__(self, requestCode=None, address=None, token=None, requestData=None) -> None:
        self.requestCode = requestCode
        self.token = token
        self.address = address
        self.requestData = requestData
    
    def getRequestCode(self):
        return self.requestCode
    
    def getToken(self):
        return self.token
    
    def getAddress(self):
        return self.address
    
    def getRequestData(self):
        return self.requestData

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
        
        return Request(requestCode=requestCode, address=address, token=token, requestData=requestData)

    def getRequestAsArray(self):
        returnData = {
            'requestCode': self.requestCode,
            'token': self.token,
            'requestData': self.requestData
        }

        return returnData
