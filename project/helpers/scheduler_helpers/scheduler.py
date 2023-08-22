import subprocess
import time


def scheduler(total_time, interval_time):
    """
    Run the RSS Feed Aggregator at a set interval.
    """

    p = subprocess.Popen(["caffeinate", "-t", str(total_time)])

    while True:
        retcode = p.poll()

        if retcode is not None:
            print("Caffeinate process has terminated.")
            return False

        time.sleep(interval_time)
        yield True
