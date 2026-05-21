import os
import subprocess
import pickle
import marshal

def dangerous_actions():
    # Dangerous OS calls
    os.system("rm -rf /")
    os.popen("ls -la")

    # Dangerous subprocess calls with shell=True
    subprocess.run("ls", shell=True)
    subprocess.call("echo 'hello'", shell=True)
    subprocess.Popen("cat /etc/passwd", shell=True)

    # Safe subprocess calls (should not be flagged)
    subprocess.run(["ls", "-l"], shell=False)
    subprocess.call(["echo", "safe"])

    # Insecure deserialization
    pickle.loads(b"some_data")
    marshal.load(open("some_file", "rb"))

    # Classic eval/exec
    eval("1 + 1")
    exec("import os")
