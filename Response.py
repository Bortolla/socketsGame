# Classe utilizada para criar respostas do servidor para o cliente
class Response:
    def __init__(self, responseCode=None, token=None, returnData=None) -> None:
        self.responseCode = responseCode    # codigo status da resposta
        self.token = token                  # token da sala
        self.returnData = returnData        # dados da resposta

    # retorna o codigo da resposta
    def getResponseCode(self):
        return self.responseCode
    
    # retorna o token da sala
    def getToken(self):
        return self.token
    
    # retorna os dados da resposta
    def getReturnData(self):
        return self.returnData

    # cria um dicionario com base nos atributos de uma instancia de Response
    def getResponseAsArray(self):
        returnData = {
            'responseCode': self.responseCode,
            'token': self.token,
            'returnData': self.returnData,
        }

        return returnData  # dicionario

    # cria uma instancia da classe Response com base em um dicionario
    def createResponseFromArray(self, array):
        # se um campo X estiver no dicionario, entao eh passado o seu valor
        # como atributo na instancia da classe Request, 
        # caso contrario, eh atribuido o valor None
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
        
        # instancia da classe Response
        return Response(responseCode=responseCode, token=token, returnData=returnData)
    