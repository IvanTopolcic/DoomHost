from threading import Thread
import configparser
import servermonitor
import sys
import tcplistener
import huffman


# The main class used for controlling the application
class DoomHost:
    # Program Entry Point
    @staticmethod
    def main():
        hm = huffman.HuffmanObject(huffman.SKULLTAG_FREQS)
        # Read our configuration file
        print("Reading configuration file...")
        config = configparser.ConfigParser()
        config.read(sys.argv[1])
        print("Loaded configuration.")
        # Start the main DoomHost object
        doomhost = DoomHost(config, hm)
        # Start the TCP Server
        print("Starting TCP listener...")
        server = tcplistener.TCPServer((config['Network']['ip_address'], int(config['Network']['port'])),
                                       tcplistener.TCPServerHandler, doomhost)
        tcp_thread = Thread(target=server.serve_forever)
        tcp_thread.start()
        print("Networking started.")
        # Start the server monitor (to kill servers using excessive usage)
        print("Starting server monitor thread...")
        monitor = servermonitor.Servermonitor(float(config['Advanced']['cpu_check_interval']),
                                              int(config['Advanced']['cpu_threshold']), int(config['Advanced']['mem_threshold']),
                                              doomhost)
        monitor_thread = Thread(target=monitor.start_monitor)
        monitor_thread.start()
        print("Server monitor started.")

    # Returns all of the servers
    def get_all_servers(self):
        return self.doom_servers

    # Returns all servers belonging to a user
    def get_user_servers(self, username):
        user_servers = []
        for doom_server in self.doom_servers:
            user_servers.append(doom_server)
        return user_servers

    # Returns a server with given port
    def get_server(self, port):
        for server in self.doom_servers:
            if server.port == port:
                return server
        return None

    # Constructor
    def __init__(self, config, hm):
        self.config = config
        self.huffman = hm
        self.config_file = sys.argv[1]
        self.doom_servers = []

# Start the application
if __name__ == "__main__":
    DoomHost.main()