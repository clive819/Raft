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
        self.id = str(uuid.uuid1()).split('-')[0]
        self.socket = None
        self.bufferSize = 4096
        self.port = 8888
        self.multicastGroup = '224.224.224.224'
        self.timeout = random.uniform(5, 10)
        self.heartBeatInterval = 1
        self.listenThread = None
        self.knownServer = set()
        self.lock = threading.Lock()

        # MARK: - UI
        self.window = None
        self.logEntry = None
        self.keyEntry = None
        self.valEntry = None

        # MARK: - raft
        self.state = FOLLOWER
        self.term = 0
        self.voteFor = None
        self.database = {}
        self.votes = set()

    def log(self, message):
        self.lock.acquire()
        self.logEntry.config(state=tk.NORMAL)
        self.logEntry.insert(tk.END, f'{message}\n')
        self.logEntry.see(tk.END)
        self.logEntry.config(state=tk.DISABLED)
        self.lock.release()

    def multicast(self, rpc):
        if self.socket is not None:
            self.socket.sendto(json.dumps(rpc).encode(), (self.multicastGroup, self.port))

    def decodeMessage(self, rpc):
        if rpc:
            rpc = RPC._make(json.loads(rpc.decode()))
            if rpc.id == self.id:
                return None

            self.knownServer.add(rpc.id)
            if rpc.term > self.term:
                self.term = rpc.term
                self.becomeFollower()

            if self.state == FOLLOWER and rpc.state != FOLLOWER:
                if rpc.state == LEADER:
                    if rpc.command == 'append' and rpc.data:
                        self.log('Ok')
                        self.database.update(rpc.data)
                    elif 'to ' in rpc.command and self.id == rpc.command.split(' ')[-1]:
                        self.log('Got it, thanks!')
                        self.database.update(rpc.data)

                    if len(self.database) < rpc.index:
                        self.log("Hey, I'm missing some data")
                        self.multicast(RPC(self.term, self.id, self.state, 'miss', len(self.database), ''))
                else:
                    if rpc.command == 'vote' and self.voteFor is None:
                        self.multicast(RPC(self.term, self.id, self.state, f'vote for {rpc.id}', len(self.database), ''))
            elif self.state == CANDIDATE:
                if 'vote for ' in rpc.command and self.id == rpc.command.split(' ')[-1]:
                    self.log(f'Collect vote from {rpc.id}')
                    self.votes.add(rpc.id)
                elif rpc.state == LEADER:
                    self.becomeFollower()
            elif self.state == LEADER:
                if rpc.state == FOLLOWER:
                    if rpc.command == 'append' and rpc.data:
                        self.database.update(rpc.data)
                        self.log('Everyone update ur database')
                        self.multicast(RPC(self.term, self.id, self.state, 'append', len(self.database), rpc.data))
                    elif rpc.command == 'miss':
                        self.log('Ok, sending it to u')
                        self.multicast(RPC(self.term, self.id, self.state, f'to {rpc.id}', len(self.database), self.database))

    def listen(self):
        while self.socket is not None:
            try:
                data, _ = self.socket.recvfrom(self.bufferSize)
                threading.Thread(target=self.decodeMessage, args=(data,), daemon=True).start()
            except socket.timeout:
                if self.socket is not None:
                    self.becomeCandidate()

    def sendHeartBeat(self):
        clock = threading.Event()
        while self.state == LEADER:
            self.multicast(RPC(self.term, self.id, self.state, 'append', len(self.database), ''))
            clock.wait(self.heartBeatInterval)

    def becomeFollower(self):
        self.state = FOLLOWER
        self.voteFor = None
        self.updateWindowTitle()

    def becomeLeader(self):
        self.state = LEADER
        self.voteFor = None
        threading.Thread(target=self.sendHeartBeat, daemon=True).start()
        self.updateWindowTitle()

    def becomeCandidate(self):
        self.term += 1
        self.voteFor = None
        self.state = CANDIDATE
        self.updateWindowTitle()
        self.votes.clear()
        self.votes.add(self.id)
        self.log('Vote me please 0.0')
        self.multicast(RPC(self.term, self.id, self.state, 'vote', len(self.database), ''))
        threading.Thread(target=self.checkVotes, daemon=True).start()

    def checkVotes(self):
        while self.state == CANDIDATE:
            if len(self.votes) >= (len(self.knownServer) // 2):
                self.becomeLeader()

    def commit(self):
        if self.keyEntry is not None:
            data = {self.keyEntry.get(): self.valEntry.get()}
            if self.state == LEADER:
                self.database.update(data)
            self.multicast(RPC(self.term, self.id, self.state, 'append', len(self.database), data))

    def retrieveFroKey(self):
        key = self.keyEntry.get()
        if key in self.database:
            val = self.database[key]
        else:
            val = 'No Match'
        self.valEntry.delete(0, tk.END)
        self.valEntry.insert(0, val)

    def updateWindowTitle(self):
        self.log(f'State: {self.state}')
        self.window.title(f'{self.state} - {self.id}')

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
                self.log(f'Unable to bind establish server')
        else:
            self.socket.close()
            self.socket = None
            self.listenThread.join()
            toggleBtn.config(text='Start Server')
            self.log('Server stopped')
            window.title('Raft Demo')
