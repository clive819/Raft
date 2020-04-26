from collections import namedtuple


LEADER = 'Leader'
FOLLOWER = 'Follower'
CANDIDATE = 'Candidate'
AppendEntry = 'append entry'
MissingData = 'missing data'
Vote = 'vote'
UpdateServerList = 'update server list'

RPC = namedtuple('RPC', ['term', 'id', 'state', 'command', 'index', 'data'])
