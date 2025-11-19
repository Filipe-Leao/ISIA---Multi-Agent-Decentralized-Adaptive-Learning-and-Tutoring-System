import csv
from datetime import datetime

class MetricsLogger:
    def __init__(self, filename="metrics.csv"):
        self.filename = filename

        with open(self.filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "student",
                "tutor",
                "topic",
                "general_progress",
                "response_time",
                "proposals_received",
                "chosen_tutor",
                "rejected_count",
                "peer_used"
            ])

    def log(self, student, tutor, topic, general_progress, response_time, proposals_received, chosen_tutor, rejected_count, peer_used):
        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now(),
                student,
                tutor,
                topic,
                general_progress,
                response_time,
                proposals_received,
                chosen_tutor,
                rejected_count,
                peer_used
            ])
