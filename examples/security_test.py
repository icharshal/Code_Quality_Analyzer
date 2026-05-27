import tempfile
import os

def insecure_temp():
    # This should be flagged as a critical security issue
    tmp = tempfile.mktemp()
    with open(tmp, 'w') as f:
        f.write("hello")

if __name__ == "__main__":
    insecure_temp()
