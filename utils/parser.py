import re


THREAD_HEADER = re.compile(
    r"^Thread\s+(?P<thread_id>\d+)\s+(?P<thread_name>.+)\s+\(lcore\s+(?P<thread_lcore>\d+)\)$"
)

TIME_THREAD = re.compile(
    r"^Time\s+(?P<time>\d+(?:\.\d+)?),\s+10 sec internal node vector rate\s+(?P<vector_rate>\d+(?:\.\d+)?)\s+loops/sec\s+(?P<loops_per_sec>\d+(?:\.\d+)?)$"
)

VECTOR_THREAD = re.compile(
    r"^vector rates in\s+(?P<in>\S+),\s+out\s+(?P<out>\S+),\s+drop\s+(?P<drop>\S+),\s+punt\s+(?P<punt>\S+)$"
)


def parse_show_runtime(raw_text: str) -> dict:
    result = {"threads": []}
    current_thread = None

    for line in raw_text.splitlines():
        stripped_line = line.strip()

        thread_match = THREAD_HEADER.match(stripped_line)
        time_thread_match = TIME_THREAD.match(stripped_line)
        vector_thread_match = VECTOR_THREAD.match(stripped_line)

        # Начало нового блока thread: перед переключением сохраняем предыдущий.
        if thread_match:
            if current_thread is not None:
                result["threads"].append(current_thread)

            current_thread = {
                "id": int(thread_match.group("thread_id")),
                "name": thread_match.group("thread_name"),
                "lcore": int(thread_match.group("thread_lcore")),
                "table_lines": [],
            }
            continue

        # До первого найденного thread полезных данных для сохранения нет.
        if current_thread is None:
            continue

        # Сохраняем метрики thread, если строка соответствует ожидаемому формату.
        if time_thread_match:
            current_thread["time"] = float(time_thread_match.group("time"))
            current_thread["internal_node_vector_rate"] = float(
                time_thread_match.group("vector_rate")
            )
            current_thread["loops_per_sec"] = float(
                time_thread_match.group("loops_per_sec")
            )
            continue

        # Сохраняем агрегированные vector rates, если они присутствуют в блоке.
        if vector_thread_match:
            current_thread["vector_rates"] = {
                "in": float(vector_thread_match.group("in")),
                "out": float(vector_thread_match.group("out")),
                "drop": float(vector_thread_match.group("drop")),
                "punt": float(vector_thread_match.group("punt")),
            }
            continue

        # Все прочие непустые строки сохраняем как исходный табличный вывод блока.
        if stripped_line:
            current_thread["table_lines"].append(line)

    # После завершения прохода сохраняем последний собранный thread.
    if current_thread is not None:
        result["threads"].append(current_thread)

    return result
