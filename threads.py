import zipfile
import base64
import threading
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import multiprocessing


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

xml_file_path = 'a-prev.xml'
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
                        <solicitud>{zipfile_base64_encoded}</solicitud>
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
        return response

def brute_force_codigo(start_range, end_range, found_event):
    client = PoliEspClient("B21579990", 'Temporal1')
    
    for codigo in range(start_range, end_range, 1):
        if found_event.is_set():
            print(f"Stopping thread for range {start_range}-{end_range} as code was found")
            break
            
        response = client.perform_action(codigo)
        from time import sleep
        sleep(1)
        print(f"Trying codigo: {str(codigo).zfill(10)}")
        
        if "codigo>10107<" not in response.text:
            print(f"Success! Found working codigo: {str(codigo).zfill(10)}")
            print(f"Response: {response.text}")
            found_event.set()  # Signal other threads to stop
            break
        print(f"Response: {response.text}")

def get_optimal_thread_count():
    cpu_threads = multiprocessing.cpu_count()
    print(f"Available CPU threads: {cpu_threads}")
    # Using a conservative number (75%) of available threads to avoid overloading
    return max(1, int(cpu_threads * 0.75))

def run_threaded_search(start, end, num_threads=None):
    if num_threads is None:
        num_threads = get_optimal_thread_count()
    print(f"Running with {num_threads} threads")
    
    found_event = Event()
    range_size = (end - start) // num_threads
    ranges = []
    
    # Create ranges for each thread
    for i in range(num_threads):
        range_start = start + (i * range_size)
        range_end = range_start + range_size if i < num_threads - 1 else end
        ranges.append((range_start, range_end))
        print(f"Thread {i+1} will check range: {range_start} - {range_end}")
        # Create and start threads
        
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(brute_force_codigo, range_start, range_end, found_event)
            for range_start, range_end in ranges
        ]
        
        # Wait for either all threads to complete or one thread to find the code
        for future in futures:
            future.result()
    
    # Rest of the function remains the same...

# Add command line argument handling
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python script.py start_range end_range [num_threads]")
        sys.exit(1)
    
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    num_threads = int(sys.argv[3]) if len(sys.argv) > 3 else None
    run_threaded_search(start, end, num_threads)