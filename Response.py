class Response:
    def __init__(self, responseCode=None, token=None, returnData=None) -> None:
        self.responseCode = responseCode # codigo da resposta
        self.token = token # token da sala
        self.returnData = returnData # dados da resposta

    def getResponseCode(self):
        return self.responseCode
    
    def getToken(self):
        return self.token
    
    def getReturnData(self):
        return self.returnData

    # Retorna resposta em formato de dicionario
    def getResponseAsArray(self):
        returnData = {
            'responseCode': self.responseCode,
            'token': self.token,
            'returnData': self.returnData,
        }

        return returnData

    # Retorna um objeto do tipo Response 
    def createResponseFromArray(self, array):
        if 'responseCode' in array:
            responseCode = array['responseCode']
        else:
            responseCode = None
        if 'token' in array:
            token = array['token']
        else:
            token = None
        if 'returnData' in array:
            returnData = array['returnData']
        else:
            returnData = None
        
        return Response(responseCode=responseCode, token=token, returnData=returnData)
    