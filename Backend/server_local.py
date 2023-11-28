# server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from urllib.parse import urlparse, parse_qs
from model import Habitacion, RobotLimpieza, Celda, Mueble, Cargador, Llegada, Salida, Estanteria, Sitio_espera
import mesa
import time

# RUN THIS FILE TO OPEN SERVER

# Size of the board:
width = 50
height = 50

# Initiate model
Model = Habitacion(width, height, num_agentes=10)

#server.launch(open_browser=True)
class Server(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        # Parse the query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Check if 'num_agentes' parameter is provided
        if 'num_agentes' in query_params:
            try:
                num_agentes = int(query_params['num_agentes'][0])

                # Reset the model
                Model.reset(num_agentes=num_agentes)
                print(f"Number of robots set to: {num_agentes}")
                print("Model reset")
            except ValueError:
                print("Invalid value for 'num_agentes'. It must be an integer.")

        # Send a response
        self._set_response()
        self.wfile.write("GET request received".encode('utf-8'))

    def do_POST(self):
        try:
            Model.step()
            positions_json = Model.positions_to_json()
            # Send the JSON response
            self._set_response()
            self.wfile.write(positions_json.encode('utf-8'))
        except Exception as e:
            print(f"Error processing POST request: {e}")
            self.send_error(400, "Bad Request")
    

def run(server_class=HTTPServer, handler_class=Server, port=8585):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print("Starting httpd...\n")
    
    # Create a thread to run the server
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.daemon = True  # Daemonize thread to make sure it's terminated when the main program exits
    server_thread.start()
    
    try:
        # Keep the main thread alive while the server thread is running
        while True:
            time.sleep(1)  # Add a delay to control the rate at which the main thread checks
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print("Stopping httpd...\n")

if __name__ == '__main__':
    run()