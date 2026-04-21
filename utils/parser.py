import re


class Parser:
    THREAD_NAME_REGEX = re.compile(
        r"^Thread\s+(?P<thread_id>\d+)\s+(?P<thread_name>.+)\s+\(lcore\s+(?P<thread_lcore>\d+)\)$"
    )
    THREAD_TIME_REGEX = re.compile(
        r"^Time\s+(?P<time>\d+(?:\.\d+)?),\s+10 sec internal node vector rate\s+(?P<vector_rate>\d+(?:\.\d+)?)\s+loops/sec\s+(?P<loops_per_sec>\d+(?:\.\d+)?)$"
    )
    THREAD_VECTOR_REGEX = re.compile(
        r"^vector rates in\s+(?P<in>\S+),\s+out\s+(?P<out>\S+),\s+drop\s+(?P<drop>\S+),\s+punt\s+(?P<punt>\S+)$"
    )

    @staticmethod
    def normalize_raw_text(raw_text):
        for line in raw_text.splitlines():
            yield line.strip()

    @staticmethod
    def parse_thread_name(match):
        return {
            "id": match.group("thread_id"),
            "name": match.group("thread_name"),
            "lcore": match.group("thread_lcore"),
        }

    @staticmethod
    def parse_thread_time(match):
        return {
            "time": match.group("time"),
            "vector_rate": match.group("vector_rate"),
            "loops_per_sec": match.group("loops_per_sec"),
        }

    @staticmethod
    def parse_thread_vector(match):
        return {
            "in": float(match.group("in")),
            "out": float(match.group("out")),
            "drop": float(match.group("drop")),
            "punt": float(match.group("punt")),
        }

    def parse_show_runtime(self, raw_text):
        result = []
        current_thread = None

        for line in self.normalize_raw_text(raw_text):
            name_match = self.THREAD_NAME_REGEX.match(line)
            if name_match:
                current_thread = self.parse_thread_name(name_match)
                result.append(current_thread)
                continue

            time_match = self.THREAD_TIME_REGEX.match(line)
            if time_match and current_thread is not None:
                current_thread.update(self.parse_thread_time(time_match))
                continue

            vector_match = self.THREAD_VECTOR_REGEX.match(line)
            if vector_match and current_thread is not None:
                current_thread.update(self.parse_thread_vector(vector_match))
                continue

            if current_thread is not None and line:
                current_thread.setdefault("table_lines", []).append(line)

        return result
