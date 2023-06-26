# Classe utilizada para criar requisicoes do cliente para o servidor
class Request:
    def __init__(self, requestCode=None, address=None, connection=None, token=None, requestData={}) -> None:
        self.requestCode = requestCode      # codigo da ação desejada
        self.token = token                  # token da sala
        self.address = address              # endereco do cliente
        self.connection = connection        # objeto socket com a conexao do cliente
        self.requestData = requestData      # dados enviados na requisicao
    
    # retorna o codigo de uma requisicao
    def getRequestCode(self):
        return self.requestCode
    
    # retorna o token da sala enviado em uma requisicao
    def getToken(self):
        return self.token
    
    # retorna o endereço do cliente
    def getAddress(self):
        return self.address
    
    # retorna os dados enviados na requisicao
    def getRequestData(self):
        return self.requestData

    # retorna a conexao do cliente
    def getConnection(self):
        return self.connection

    # retorna uma instancia da classe Request com base nos dados em um dicionario
    def createRequestFromArray(self, array):
        # se um campo X estiver no dicionario, entao eh passado o seu valor
        # como atributo na instancia da classe Request, 
        # caso contrario, eh atribuido o valor None
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
        
        # instancia da classe Request
        return Request(requestCode=requestCode, address=address, connection=connection, token=token, requestData=requestData)

    # retorna um dicionario dos dados presentes em uma instancia da classe Request
    def getRequestAsArray(self):
        returnData = {
            'requestCode': self.requestCode,
            'token': self.token,
            'connection': self.connection,
            'requestData': self.requestData
        }

        return returnData # dicionario
