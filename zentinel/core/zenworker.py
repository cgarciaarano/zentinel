import sys
from rq import Queue, Connection, Worker


# Preload libraries
from zentinal.core import actions, logger


# Provide queue names to listen to as arguments to this script,
# similar to rqworker
with Connection():
    qs = map(Queue, sys.argv[1:]) or [Queue()]

    logger.debug("Initializing Zen Worker...")
    w = Worker(qs)
    w.work()