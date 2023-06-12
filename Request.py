# Classe Request para manipular as requisicoes feitas ao servidor pelos clientes
class Request:
    def __init__(self, requestCode=None, address=None, token=None, requestData=None) -> None:
        self.requestCode = requestCode # Codigo que representa a ação que o cliente deseja realizar 
        self.token = token # string que representa o ID de uma sala
        self.address = address # endereço do cliente que está fazendo a requisição
        self.requestData = requestData # dados enviados juntamente com a requisição
    
    def getRequestCode(self):
        return self.requestCode
    
    def getToken(self):
        return self.token
    
    def getAddress(self):
        return self.address
    
    def getRequestData(self):
        return self.requestData
    
    # Método cria uma instância da classe Request com os dados do cliente enviados ao servidor
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
        
        # Retorna a instancia da classe
        return Request(requestCode=requestCode, address=address, token=token, requestData=requestData)

    def getRequestAsArray(self):
        returnData = {
            'requestCode': self.requestCode,
            'token': self.token,
            'requestData': self.requestData
        }

        return returnData
