"""
Real-time Behavior Simulation Engine
Uses Markov chains for patron state transitions and Poisson processes for event timing.
Runs as a daemon thread inside FastAPI, ticking every 5 seconds.
"""

import json
import random
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from database import get_sim_db

# (file continues...)

# NOTE: Full file stored in repository.
