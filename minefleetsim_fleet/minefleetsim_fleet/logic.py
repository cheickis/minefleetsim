"""Deterministic single-segment reservation state (ROS independent)."""
class TunnelLease:
    def __init__(self):
        self.owner = None
        self.queue = []

    def request(self, robot):
        if self.owner == robot:
            return True
        if robot not in self.queue:
            self.queue.append(robot)
        if self.owner is None and self.queue[0] == robot:
            self.owner = self.queue.pop(0)
            return True
        return False

    def release(self, robot):
        if self.owner != robot:
            raise ValueError(f'{robot} does not own tunnel lease')
        self.owner = None
