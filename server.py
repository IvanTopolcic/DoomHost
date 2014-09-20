import json
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
import psutil


class Server:

    def __init__(self, doomhost, data):
        self.doomhost = doomhost
        self.data = data

    # Sets up everything to start the server
    def start_server(self):
        # Make sure we have all the settings needed to start the server
        try:
            # First, get all of the *required* entries
            self.source_port = self.data['source_port']
            self.iwad = self.data['iwad']
            self.hostname = self.data['hostname']
            self.gamemode = self.data['gamemode']
            self.port = self.data['port']
            self.starting = True
            self.stopping = False
            self.args = []
            self.wads = []
            self.skill = None
            self.config = None
            self.st_data = None
            self.autorestart = None
            self.dmflags = None
            self.dmflags2 = None
            self.dmflags3 = None
            self.compatflags = None
            self.compatflags2 = None
            # Next, collect any option parameters
            if 'wads' in self.data:
                self.wads = self.data['wads']
            if 'skill' in self.data:
                self.skill = self.data['skill']
            if 'configs' in self.data:
                self.configs = self.data['configs']
            if 'st_data' in self.data:
                self.st_wads = self.data['st_data']
            if 'autorestart' in self.data:
                self.autorestart = self.data['autorestart']
            if 'dmflags' in self.data:
                self.dmflags = self.data['dmflags']
            if 'dmflags2' in self.data:
                self.dmflags2 = self.data['dmflags2']
            if 'dmflags3' in self.data:
                self.dmflags3 = self.data['dmflags3']
            if 'compatflags' in self.data:
                self.compatflags = self.data['compatflags']
            if 'compatflags2' in self.data:
                self.compatflags2 = self.data['compatflags2']
            return self.start_server_process()
        except KeyError as e:
            # Not all information filled in
            return {'return': 'error', 'status': 'Missing: {0}'.format(e)}

    def start_server_process(self):
        Thread(target=self.server_process).start()
        self.doomhost.doom_servers.append(self)
        return {'return': 'error', 'status': 'Starting server on port {0}'.format(self.port)}

    # Starts the server
    def server_process(self):
        # Add the executable
        self.args.append(self.doomhost.config['Zandronum']['executable'])
        self.args.append("-host")
        # Add the IWAD
        self.args.append("-iwad")
        self.args.append(self.doomhost.config['Zandronum']['wad_directory'] + self.iwad)
        # Add the Gamemode
        self.args.append("-" + self.gamemode)
        self.args.append("1")
        # Add the hostname
        self.args.append("+sv_hostname")
        self.args.append(self.hostname)
        # Optional parameters
        # Add the wads
        for wad in self.wads:
            self.args.append("-file")
            self.args.append(self.doomhost.config['Zandronum']['wad_directory'] + wad)
        self.proc = psutil.Popen(self.args, stdout=PIPE, stderr=STDOUT)
        for line in self.proc.stdout:
            line = line.decode('UTF-8').rstrip()
            print(line)
            if self.starting:
                if line == "UDP Initialized.":
                    self.starting = False
                    break

    # Kills a server and removes it from the list
    def kill_server(self):
        self.stopping = True
        self.proc.kill()
        self.doomhost.doom_servers.remove(self)