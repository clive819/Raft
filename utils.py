from collections import namedtuple


LEADER = 'Leader'
FOLLOWER = 'Follower'
CANDIDATE = 'Candidate'

RPC = namedtuple('RPC', ['term', 'id', 'state', 'command', 'index', 'data'])
