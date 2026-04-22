import re


class Logs:
    def __init__(self, collected_logs):
        self.logs = self._clear_lines(collected_logs)

    def _clear_lines(self, collected_logs):
        cleared_lines = []

        for line in collected_logs.splitlines():
            line = line.strip()

            if not line or line.startswith("---"):
                continue

            if line[0].isdigit():
                cleared_lines[-1] += " " + line
            else:
                cleared_lines.append(line)

        return cleared_lines


class ShowRuntime(Logs):
    THREAD = re.compile(
        r"Thread (?P<thread_id>\d+) (?P<thread_name>\S+) \(lcore (?P<thread_lcore>\d+)\)")
    TIME = re.compile(
        r"Time (?P<thread_time>\d+\.\d+), 10 sec internal node vector rate (?P<thread_vector_rate>\d+\.\d+) loops/sec (?P<thread_loops_per_sec>\d+\.\d+)")
    VECTOR = re.compile(
        r"vector rates in (?P<thread_in>\d+\.\d+e[+-]?\d+), out (?P<thread_out>\d+\.\d+e[+-]?\d+), drop (?P<thread_drop>\d+\.\d+e[+-]?\d+), punt (?P<thread_punt>\d+\.\d+e[+-]?\d+)")
    TABLE = re.compile(
        r'(?P<table_process>\S+)\s+"?(?P<table_state>[^"]*?\S)"?\s+(?P<table_calls>\d+)\s+(?P<table_vectors>\d+)\s+(?P<table_suspends>\d+)\s+(?P<table_clocks>\d+\.\d+e[+-]?\d+)\s+(?P<table_vectors_per_call>\d+\.\d+)')

    def __init__(self, collected_logs):
        super().__init__(collected_logs)

    def parsing(self):
        threads = []
        current_thread = None

        for line in self.logs:
            thread_match = self.THREAD.match(line)
            if thread_match:
                if current_thread:
                    threads.append(current_thread)

                current_thread = {
                    "thread_id": thread_match.group("thread_id"),
                    "thread_name": thread_match.group("thread_name"),
                    "thread_lcore": thread_match.group("thread_lcore")
                }
                continue

            time_match = self.TIME.match(line)
            if time_match:
                current_thread.update(
                    {
                        "thread_time": float(time_match.group("thread_time")),
                        "thread_vector_rate": float(time_match.group("thread_vector_rate")),
                        "thread_loops_per_sec": float(time_match.group("thread_loops_per_sec"))
                    }
                )
                continue

            vector_match = self.VECTOR.match(line)
            if vector_match:
                current_thread.update(
                    {
                        "thread_in": float(vector_match.group("thread_in")),
                        "thread_out": float(vector_match.group("thread_out")),
                        "thread_drop": float(vector_match.group("thread_drop")),
                        "thread_punt": float(vector_match.group("thread_punt"))
                    }
                )
                continue

            table_match = self.TABLE.match(line)
            if table_match:
                current_thread.setdefault("table", []).append(
                    {
                        "table_process": table_match.group("table_process"),
                        "table_state": table_match.group("table_state"),
                        "table_calls": table_match.group("table_calls"),
                        "table_vectors": int(table_match.group("table_vectors")),
                        "table_suspends": table_match.group("table_suspends"),
                        "table_clocks": float(table_match.group("table_clocks")),
                        "table_vectors_per_call": float(table_match.group("table_vectors_per_call"))
                    }
                )
                continue

        if current_thread:
            threads.append(current_thread)

        return threads
