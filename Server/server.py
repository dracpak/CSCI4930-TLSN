from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import logging
from io import StringIO

log_stream = StringIO()
record = ""

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='certificate.pem', keyfile='key.pem')
context.check_hostname = False

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        try:
            fd = open(self.path[1:], 'rb')
        except OSError:
            fd = open("index.html", 'rb')
            self.path = "/index.html"
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        string = fd.read()
        self.wfile.write(string)
        record = log_stream.getvalue()

def run(server_class=HTTPServer, handler_class=S, port=4443):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')
    print(record)

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
