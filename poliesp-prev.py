import zipfile
import base64


def compress_to_zip(xml_file_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(xml_file_path)

def encode_zip_as_base64(zip_file_path):
    with open(zip_file_path, 'rb') as file:
        encoded = base64.b64encode(file.read())
        return encoded.decode('utf-8')

def compress_and_encode(xml_file_path):
    zip_file_path = 'compressed_file.zip'
    compress_to_zip(xml_file_path, zip_file_path)
    base64_encoded = encode_zip_as_base64(zip_file_path)

    return base64_encoded

xml_file_path = 'altaph.xml'
z = compress_and_encode(xml_file_path)
import pdb; pdb.set_trace()
import requests
import base64

class PoliEspClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @property
    def _auth_string(self):
        return f"{self.username}:{self.password}"
    
    def _auth_string_base64(self):
        return base64.b64encode(self._auth_string.encode('utf-8')).decode('utf-8')

    def _get_headers(self):
        return {
            "Authorization": f"Basic {self._auth_string_base64()}",
        }

    def perform_action(self, codigo_arrendador):
        """Attempt authentication with a specific codigo_arrendador"""
        # Zero pad the codigo_arrendador to length 10
        codigo_arrendador_padded = str(codigo_arrendador).zfill(10)
        
        data = f'''
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:com="http://www.soap.servicios.hospedajes.mir.es/comunicacion">
            <soapenv:Header/>
            <soapenv:Body>
                <com:comunicacionRequest>
                    <peticion>
                        <cabecera>
                        <codigoArrendador>{codigo_arrendador_padded}</codigoArrendador>
                        <aplicacion>CA</aplicacion>
                        <tipoOperacion>A</tipoOperacion>
                        <!--Optional:-->
                        <tipoComunicacion>PV</tipoComunicacion>
                        </cabecera>
                        <solicitud>{z}</solicitud>
                    </peticion>
                </com:comunicacionRequest>
            </soapenv:Body>
            </soapenv:Envelope>
        '''
        response = requests.post(
            "https://hospedajes.pre-ses.mir.es/hospedajes-web/ws/v1/comunicacion",
            data=data,
            headers=self._get_headers(),
            verify=False
        )
        import pdb; pdb.set_trace()
        return response

def brute_force_codigo():
    client = PoliEspClient("B21579990", 'Temporal1')
    
    for codigo in range(1550, 0, -1):
        response = client.perform_action(codigo)
        print(f"Trying codigo: {str(codigo).zfill(10)}")
        
        if "codigo>10107<" not in response.text:
            print(f"Success! Found working codigo: {str(codigo).zfill(10)}")
            print(f"Response: {response.text}")
            break

PoliEspClient("B21579990", 'Temporal1').perform_action(324)