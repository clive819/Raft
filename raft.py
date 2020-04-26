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
        self.leaderID = None
        self.state = FOLLOWER
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
            self.socket.sendto(json.dumps(rpc).encode(), (self.multicastGroup, self.port))

    def decodeMessage(self, rpc):
        if rpc:
            rpc = json.loads(rpc.decode())
            if rpc.id == self.id:
                return None

            if self.state == FOLLOWER:
                pass
            elif self.state == CANDIDATE:
                pass
            else:
                pass

    def listen(self):
        while self.socket is not None:
            try:
                data, _ = self.socket.recvfrom(self.bufferSize)
                t = threading.Thread(target=self.decodeMessage, args=(data,), daemon=True)
                t.start()
            except socket.timeout:
                if self.socket is not None:
                    self.voteFor = None
                    if self.state == FOLLOWER:
                        self.becomeCandidate()
                    elif self.state == CANDIDATE:
                        # FIXME
                        pass

    def claimLeader(self):
        pass

    def sendHeartBeat(self):
        pass

    def becomeFollower(self):
        self.state = FOLLOWER
        self.updateWindowTitle()
        self.term += 1
        # FIXME

    def becomeLeader(self):
        self.state = LEADER
        self.updateWindowTitle()
        self.term += 1
        # FIXME

    def becomeCandidate(self):
        self.state = CANDIDATE
        self.updateWindowTitle()
        self.term += 1
        # FIXME

    def commit(self):
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
        key = self.keyEntry.get()
        if key in self.database:
            val = self.database[key]
        else:
            val = 'No Match'
        self.valEntry.configure(text=val)

    def updateWindowTitle(self):
        self.log(f'State: {self.state}')
        self.window.title(f'{self.state} - {self.id.split("-")[0]}')

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
