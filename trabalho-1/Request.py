from datetime import datetime

class Request:
    def __init__(self, process_id: int, timestamp: datetime):
        self.process_id = process_id
        self.timestamp = timestamp

    def __repr__(self):
        return f"<Request process_id={self.process_id} timestamp={self.timestamp.strftime('%H:%M:%S')}>"
