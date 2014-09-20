import socketserver
import json
import requestprocessor


class TCPServer(socketserver.ThreadingTCPServer):
    # Make sure we pass a reference to DoomHost
    def __init__(self, server_address, RequestHandlerClass, doomhost):
        super().__init__(server_address, RequestHandlerClass, doomhost)
        self.doomhost = doomhost
    allow_reuse_address = True


# Handles receiving messages and parses the (presumably) JSON message
class TCPServerHandler(socketserver.BaseRequestHandler):
    # Reads the message we received
    def handle(self):
        try:
            data = json.loads(self.request.recv(2048).decode('UTF-8').strip())
            # Process the data
            rp = requestprocessor.RequestProcessor(data, self.server.doomhost)
            self.request.sendall(bytes(json.dumps(rp.process_request()), 'UTF-8'))
        except Exception as e:
            print("Exception while receiving message: {0}".format(e))