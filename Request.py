class Request:
    def __init__(self, requestCode=None, address=None, connection=None, token=None, tokenAddress=None, requestData=None) -> None:
        self.requestCode = requestCode

        self.token = token
        self.address = address
        self.tokenAddress = tokenAddress

        self.connection = connection
        self.requestData = requestData
    
    def getTokenAddress(self):
        return self.tokenAddress

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

        if 'tokenAddress' in array:
            tokenAddress = array['tokenAddress']
        else:
            tokenAddress = None
        
        return Request(requestCode=requestCode, address=address, connection=connection, token=token, tokenAddress=tokenAddress, requestData=requestData)

    def getRequestAsArray(self):
        returnData = {
            'requestCode': self.requestCode,
            'address': self.address,
            'token': self.token,
            'tokenAddress': self.tokenAddress,
            'connection': self.connection,
            'requestData': self.requestData
        }

        return returnData
