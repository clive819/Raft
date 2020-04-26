from collections import namedtuple


LEADER = 'leader'
FOLLOWER = 'follower'
CANDIDATE = 'candidate'


RPC = namedtuple('RPC', ['term', 'id', 'command', 'index', 'data'])



