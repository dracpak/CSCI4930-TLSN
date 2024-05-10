from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import logging
from time import localtime, strftime
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util.number import bytes_to_long
from Crypto.Hash import SHA256

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='certificate.pem', keyfile='key.pem')
context.check_hostname = False

privateKey = RSA.import_key(open('key.pem').read())

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        logging.info(str(self.responses[200]))
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if '?' not in self.path:
            try:
                fd = open(self.path[1:], 'rb')
            except OSError:
                fd = open("index.html", 'rb')
                self.path = "/index.html"
            
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            self._set_response()
            outfile = fd.read()
            self.wfile.write(outfile)
        elif ("getEvidence=true" in self.path) & ("hcn1=" in self.path):
            self.send_response(200)
            index = self.path.find("hcn1=")
            message = self.path[index+7:index+71]
            message = SHA256.new(bytes.fromhex(message))
            signed = pkcs1_15.new(privateKey).sign(message)
            f = open("signed.txt", 'w')
            f.write(hex(bytes_to_long(signed)))
            f.close()
            self.send_header("Content-type", "text/html")
            self.end_headers()
            fd = open("signed.txt", 'rb')
            outfile = fd.read()
            self.wfile.write(outfile)
        else:
            self.send_response(200)
            query = self.path.find("?")
            self.path = self.path[:query]
            print(self.path)
            try:
                fd = open(self.path[1:], 'rb')
            except OSError:
                fd = open("index.html", 'rb')
                self.path = "/index.html"
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            self._set_response()
            outfile = fd.read()
            self.wfile.write(outfile)
            

def run(server_class=HTTPServer, handler_class=S, port=4443):
    logging.basicConfig(filename='LOGFILE.log', encoding='utf-8', level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    logging.info("Starting timestamp: " + strftime("%a, %d %b %Y %H:%M:%S +0000", localtime()))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        logging.info("Ending timestamp: " + strftime("%a, %d %b %Y %H:%M:%S +0000", localtime()))

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
