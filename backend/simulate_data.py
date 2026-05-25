"""
Data Simulation for Decision Intelligence Platform Demo
Scale: 30,000 DAU (Daily Active Users)
Context: Casino / Hospitality Patron Engagement

Generates: Patrons, Wagering, Campaigns, Redemptions, Comp, Interactions,
           Sales/Hosts, Tasks, KPI snapshots, Rooms, Bookings, F&B,
           Credit Lines, Comp Transactions, AI Actions
"""

import sqlite3
import random
import uuid
import os
from datetime import datetime, timedelta
from faker import Faker

DB_PATH = os.path.join(os.path.dirname(__file__), "simulation.db")

fake = Faker()

# (file continues...)

# NOTE: Full file stored in repository.
