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

xml_file_path = 'a.xml'
zipfile_base64_encoded = compress_and_encode(xml_file_path)

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

    def perform_action(self):
        """NOTE: again, please note this was just to get a functional request..."""
        data = f'''
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:com="http://www.soap.servicios.hospedajes.mir.es/comunicacion">
            <soapenv:Header/>
            <soapenv:Body>
                <com:comunicacionRequest>
                    <alt:peticion>
                        <cabecera>
                        <codigoArrendador>0000012968</codigoArrendador>
                        <aplicacion>CA</aplicacion>
                        <tipoOperacion>C</tipoOperacion>
                        <!--Optional:-->
                        <tipoComunicacion>RH</tipoComunicacion>
                        </cabecera>
                        <solicitud>{zipfile_base64_encoded}</solicitud>
                    </alt:peticion>
                </com:comunicacionRequest>
            </soapenv:Body>
            </soapenv:Envelope>
        '''
        response = requests.post(
            "https://hospedajes.ses.mir.es/hospedajes-web/ws/v1/comunicacion",
            data=data,
            headers=self._get_headers(),
            verify=False
        )
        import pdb; pdb.set_trace()
        print(response.text)
        return response


PoliEspClient("48951733MWS", 'A},"+NVs').perform_action()
