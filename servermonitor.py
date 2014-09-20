from time import sleep

# Class responsible for monitoring active servers and shutting down
# any that use too many resources.
class Servermonitor:
    # Constructor
    def __init__(self, interval, cpu_threshold, mem_threshold, doomhost):
        self.interval = interval
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.doomhost = doomhost

    # Checks to see if any servers are using too many resources
    def start_monitor(self):
        while True:
            for doom_server in self.doomhost.doom_servers:
                if not doom_server.starting and not doom_server.stopping and doom_server.proc.get_cpu_percent(interval=self.interval) > self.cpu_threshold:
                    try:
                        #doom_server.kill_server()
                        doom_server.rcon.connect()
                    except:
                        continue