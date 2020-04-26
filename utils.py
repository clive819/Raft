from collections import namedtuple
from enum import Enum


class ServerState(Enum):
    Leader = 'leader'
    Follower = 'follower'
    Candidate = 'candidate'


RPC = namedtuple('RPC',
                 ['term', 'id', ''])



