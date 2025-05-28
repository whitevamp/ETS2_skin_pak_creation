from threading import Thread
try:
    from monotonic import monotonic
except ModuleNotFoundError:
    from time import monotonic
import backoff
import json

if __name__ == "__main__":
    from request import post, APIError, DatetimeSerializer
else:
    from .request import post, APIError, DatetimeSerializer

try:
    from queue import Empty
except ImportError:
    from Queue import Empty

MAX_MSG_SIZE = 32 << 10

# Our servers only accept batches less than 500KB. Here limit is set slightly
# lower to leave space for extra data that will be added later, eg. "sentAt".
BATCH_SIZE_LIMIT = 475000


class Consumer(Thread):
    def __init__(self, queue, write_key, flush_at=100, host=None,
                 on_error=None, flush_interval=0.5, retries=10, timeout=15):
        """Create a consumer thread."""
        Thread.__init__(self)
        # Make consumer a daemon thread so that it doesn't block program exit
        self.daemon = True
        self.flush_at = flush_at
        self.flush_interval = flush_interval
        self.write_key = write_key
        self.host = host
        self.on_error = on_error
        self.queue = queue
        # It's important to set running in the constructor: if we are asked to
        # pause immediately after construction, we might set running to True in
        # run() *after* we set it to False in pause... and keep running
        # forever.
        self.running = True
        self.retries = retries
        self.timeout = timeout

    def run(self):
        """Runs the consumer."""
        while self.running:
            self.upload()

    def pause(self):
        """Pause the consumer."""
        self.running = False

    def upload(self):
        """Upload the next batch of items, return whether successful."""
        success = False
        batch = self.next()
        if len(batch) == 0:
            return False

        try:
            self.request(batch)
            success = True
        except Exception as e:
            print("Error uploading analytics data")
            success = False
            if self.on_error:
                self.on_error(e, batch)
        finally:
            # mark items as acknowledged from queue
            print("...finished sending")
            for item in batch:
                self.queue.task_done()
            return success

    def next(self):
        """Return the next batch of items to upload."""
        queue = self.queue
        items = []

        start_time = monotonic()
        total_size = 0

        while len(items) < self.flush_at:
            elapsed = monotonic() - start_time
            if elapsed >= self.flush_interval:
                break
            try:
                item = queue.get(
                    block=True, timeout=self.flush_interval - elapsed)
                item_size = len(json.dumps(
                    item, cls=DatetimeSerializer).encode())
                if item_size > MAX_MSG_SIZE:
                    print("Analytics data > 32 KB, cannot upload")
                    continue
                items.append(item)
                total_size += item_size
                if total_size >= BATCH_SIZE_LIMIT:
                    print("Total analytics data > 500 KB, cannot upload")
                    break
            except Empty:
                break

        return items

    def request(self, batch):
        """Attempt to upload the batch and retry before raising an error """

        def fatal_exception(exc):
            if isinstance(exc, APIError):
                # retry on server errors and client errors
                # with 429 status code (rate limited),
                # don't retry on other client errors
                return (400 <= exc.status < 500) and exc.status != 429
            else:
                # retry on all other errors (eg. network)
                return False

        @backoff.on_exception(
            backoff.expo,
            Exception,
            max_tries=self.retries + 1,
            giveup=fatal_exception)
        def send_request():
            post(self.write_key, self.host, timeout=self.timeout, batch=batch)

        send_request()
