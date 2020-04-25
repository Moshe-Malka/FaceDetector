
import time, os, random
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher(FileSystemEventHandler):
    def __init__(self, path, verbose=False):
        self.s3_client = boto3.client('s3')
        self.bucket_name = "my-test-bkt-123"

        self.verbose = verbose
        self.wait_duration = 5
        self.min_files = 10
        self.amount_to_send = 1
        self.known_folders = []

        self.observer = Observer()
        self.dir_to_watch = path
        self.event_handler = self

    def upload_images(self, files):
        for f in files:
            try:
                with open(f, 'rb') as fd:
                    response = self.s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=f"images/{f.split('images/')[1]}",
                        Body=fd
                    )
                if self.verbose: print(f"Response : {response}")
                if response['ResponseMetadata']['HTTPStatusCode'] == 200: print(f"Put object succeded - {f}")
                else: print(f"Put object failed - {f}")
            except OSError as ose:
                print(f"Error reading file - {path}")
                print(ose)
            except ClientError as ce:
                print(f"Error trying to upload file - {path}")
                print(ce)

    def on_created(self, event):
        path = event.src_path
        if event.is_directory and 'minute' in path and path not in self.known_folders:
            if self.verbose: print(f"New Path : {path}")
            self.known_folders.append(path)
            time.sleep(self.wait_duration)
            files = [ f"{path}/{x}" for x in os.listdir(path) ]
            if len(files) < self.min_files: print(f"Not enough files found ({len(files)}) - Skipping...")
            else:
                rand_files = random.choices(files, k=self.amount_to_send)
                if self.verbose: print(f"Random files: {rand_files}")
                self.upload_images(rand_files)
                time.sleep(self.wait_duration)
                                    
    def run(self):
        self.observer.schedule(self.event_handler, self.dir_to_watch, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print(f"\n<{datetime.now()}> Stoping Watcher (KeyboardInterrupt)...")
        except Exception as e:
            self.observer.stop()
            print(f"\n<{datetime.now()}> Stoping Watcher (Generic Exception)...")
            print(f"\nError : {e}")

        self.observer.join()

    def on_any_event(self, event):
        if self.verbose: print(f"Event : {event}")

if __name__ == '__main__':
    print(f"<{datetime.now()}> Starting Watcher...")
    # w = Watcher(path="/Users/moshemalka/Downloads/deep-learning-face-detection/images/")
    w = Watcher(path="/Users/moshemalka/Downloads/deep-learning-face-detection/images/", verbose=True)
    w.run()