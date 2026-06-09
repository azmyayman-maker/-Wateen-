import time

from django_redis import get_redis_connection

MAX_CONNECTIONS_PER_AGENCY = 5
HEARTBEAT_TIMEOUT = 15  # seconds

class ConnectionTracker:
    @staticmethod
    def add_connection(agency_id, session_id):
        redis_conn = get_redis_connection("default")
        key = f"dashboard:conns:{agency_id}"
        now = int(time.time())

        # O(log(N)) cleanup of dead zombie connections explicitly on connect
        redis_conn.zremrangebyscore(key, "-inf", now - HEARTBEAT_TIMEOUT)

        current_count = redis_conn.zcard(key)
        if current_count >= MAX_CONNECTIONS_PER_AGENCY:
            return False

        redis_conn.zadd(key, {session_id: now})
        redis_conn.expire(key, 86400) # absolute upper bound generic safety
        return True

    @staticmethod
    def heartbeat_connection(agency_id, session_id):
        """Called every broadcast loop to indicate the socket is still alive."""
        redis_conn = get_redis_connection("default")
        key = f"dashboard:conns:{agency_id}"
        redis_conn.zadd(key, {session_id: int(time.time())})

    @staticmethod
    def remove_connection(agency_id, session_id):
        redis_conn = get_redis_connection("default")
        key = f"dashboard:conns:{agency_id}"
        redis_conn.zrem(key, session_id)
