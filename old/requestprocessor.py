import server


# Reads the message and performs the appropriate action
class RequestProcessor:
    # Constructor
    def __init__(self, message, doomhost):
        self.message = message
        self.doomhost = doomhost

    # Check the action received and perform the appropriate operation
    def process_request(self):
        if self.message.get("action") == "host":
            doom_server = server.Server(self.doomhost, self.message)
            return doom_server.start_server()
        elif self.message.get("action") == "kill":
            if 'port' in self.message:
                doom_server = self.doomhost.get_server(self.message['port'])
                if doom_server is None:
                    return {'return': 'error', 'status': 'There is no server running on {0}.'.format(self.message['port'])}
                else:
                    doom_server.kill_server()
                    return {'return': 'success', 'status': 'Killed server running on port {0}.'.format(doom_server.port)}
            else:
                return {'return': 'error', 'status': 'Malformed message received.'}
        else:
            None