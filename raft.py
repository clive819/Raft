from utils import *
import tkinter as tk
import threading
import socket
import struct
import random
import uuid
import json


class Raft(object):
    def __init__(self):
        self.id = str(uuid.uuid1())
        self.socket = None
        self.bufferSize = 4096
        self.port = 8888
        self.multicastGroup = '224.224.224.224'
        self.timeout = random.uniform(5, 10)
        self.listenThread = None
        self.knownServer = set()

        # MARK: - UI
        self.window = None
        self.logEntry = None
        self.keyEntry = None
        self.valEntry = None

        # MARK: - raft
        self.state = ServerState.Follower
        self.term = -1
        self.voteFor = None
        self.database = {}

    def log(self, message):
        self.logEntry.config(state=tk.NORMAL)
        self.logEntry.insert(tk.END, f'{message}\n')
        self.logEntry.see(tk.END)
        self.logEntry.config(state=tk.DISABLED)

    def multicast(self, rpc):
        if self.socket is not None:
            pass
            # self.socket.sendto(json.dumps(d).encode(), (self.multicastGroup, self.port))

    def decodeMessage(self, data):
        # TODO: handle request e.g. heartbeat, RPC
        # MARK: - test
        if data:
            data = data.decode()
            data = json.loads(data)
            if data['id'] != self.id:
                self.log(data)

    def listen(self):
        while self.socket is not None:
            try:
                data, _ = self.socket.recvfrom(self.bufferSize)
                t = threading.Thread(target=self.decodeMessage, args=(data,), daemon=True)
                t.start()
            except socket.timeout:
                if self.socket is not None:
                    if self.state == ServerState.Follower:
                        self.becomeCandidate()
                    elif self.state == ServerState.Candidate:
                        # FIXME
                        pass

    def claimLeader(self):
        pass

    def sendHeartBeat(self):
        pass

    def becomeFollower(self):
        self.state = ServerState.Follower
        self.updateWindowTitle()
        self.voteFor = None
        self.term += 1
        # FIXME

    def becomeLeader(self):
        self.state = ServerState.Leader
        self.updateWindowTitle()
        # FIXME

    def becomeCandidate(self):
        self.state = ServerState.Candidate
        self.updateWindowTitle()
        # FIXME

    def appendKeyVal(self):
        # TODO: check state
        if self.keyEntry is not None:
            pass
            # d = {
            #     'key': self.keyEntry.get(),
            #     'val': self.valEntry.get(),
            #     'command': 'append'
            # }
            # self.multicast(d)

    def retrieveFroKey(self):
        pass

    def updateWindowTitle(self):
        self.log(f'State: {self.state.value}')
        self.window.title(f'{self.state.value} - {self.id.split("-")[0]}')

    def toggleServer(self, *args):
        window, keyEntry, valEntry, toggleBtn, log = args
        self.logEntry = log
        self.window = window
        self.keyEntry = keyEntry
        self.valEntry = valEntry

        if self.socket is None:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                self.socket.bind(('', self.port))

                # MARK: - setup IP multicast
                mreq = struct.pack('4sL', socket.inet_aton(self.multicastGroup), socket.INADDR_ANY)
                self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

                self.socket.settimeout(self.timeout)
                self.becomeFollower()

                self.listenThread = threading.Thread(target=self.listen, daemon=True)
                self.listenThread.start()

                toggleBtn.config(text='Stop Server')
            except:
                self.socket = None
                self.log(f'unable to bind establish server')
        else:
            self.socket.close()
            self.socket = None
            self.listenThread.join()
            toggleBtn.config(text='Start Server')
            self.log('server stopped')
            window.title('Raft Demo')
