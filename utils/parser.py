import re


class Parser:
    THREAD_NAME_REGEX = re.compile(
        r'^Thread (?P<thread_id>\d+) (?P<thread_name>\S+) \(lcore (?P<thread_lcore>\d+)\)$')
    THREAD_TIME_REGEX = re.compile(
        r'^Time (?P<time>\d+\.\d+), 10 sec internal node vector rate (?P<vector_rate>\d+\.\d+) loops/sec (?P<loops_per_sec>\d+\.\d+)$')
    THREAD_VECTOR_REGEX = re.compile(
        r'^vector rates in (?P<in>\d+\.\d+e[+-]?\d+), out (?P<out>\d+\.\d+e[+-]?\d+), drop (?P<drop>\d+\.\d+e[+-]?\d+), punt (?P<punt>\d+\.\d+e[+-]?\d+)$')
    TABLE_ROW_REGEX = re.compile(
        r'^(?P<name>.+?)\s*"?(?P<state>event wait|any wait|one time event wait|clock wait|interrupt wait|not started|suspended|running|polling|active|disabled|done|yield)"?\s+(?P<calls>\d+)\s+(?P<vectors>\d+)\s+(?P<suspends>\d+)\s+(?P<clocks>\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s+(?P<vectors_per_call>\d+\.\d+)$')

    @staticmethod
    def normalize_raw_text(raw_text):
        for line in raw_text.splitlines():
            yield line.strip()

    @staticmethod
    def is_table_header_line(line):
        return (
            (
                "Name" in line
                and "State" in line
                and "Calls" in line
                and "Vectors" in line
            )
            or (
                "Clocks" in line
                and "Vectors/Call" in line
            )
        )

    @staticmethod
    def is_table_separator_line(line):
        return line.startswith("---")

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

    @staticmethod
    def parse_table_row(match):
        return {
            "name": match.group("name"),
            "state": match.group("state"),
            "calls": match.group("calls"),
            "vectors": match.group("vectors"),
            "suspends": match.group("suspends"),
            "clocks": float(match.group("clocks")),
            "vectors_per_call": match.group("vectors_per_call"),
        }

    def parse_thread_table(self, table_lines):
        table_rows = []
        row_text = ""

        for line in table_lines:
            if self.is_table_separator_line(line) or self.is_table_header_line(line):
                row_text = ""
                continue

            row_text = f"{row_text} {line}".strip()
            match = self.TABLE_ROW_REGEX.match(row_text)

            if match:
                table_rows.append(self.parse_table_row(match))
                row_text = ""

        return table_rows

    def parse_show_runtime(self, raw_text):
        threads = []
        current_thread = None

        for line in self.normalize_raw_text(raw_text):
            name_match = self.THREAD_NAME_REGEX.match(line)
            if name_match:
                current_thread = self.parse_thread_name(name_match)
                threads.append(current_thread)
                continue

            if current_thread is None:
                continue

            time_match = self.THREAD_TIME_REGEX.match(line)
            if time_match:
                current_thread.update(self.parse_thread_time(time_match))
                continue

            vector_match = self.THREAD_VECTOR_REGEX.match(line)
            if vector_match:
                current_thread.update(self.parse_thread_vector(vector_match))
                continue

            current_thread.setdefault("table_lines", []).append(line)

        for thread in threads:
            thread["table_rows"] = self.parse_thread_table(
                thread.pop("table_lines"))

        return threads
