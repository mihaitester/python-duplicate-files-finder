import os
import shutil
import unittest

import subprocess
import threading
import time

BASE_FOLDER = os.path.abspath(os.path.dirname(__file__))
TEST_FOLDER = os.path.join(BASE_FOLDER, "scrap_test_folder")
SCRIPT = "duplicate-finder.cmd"
ENCODING = "UTF-8"

THREAD_STDOUT = b""
THREAD_STDERR = b""
THREAD_SLEEP = 2

def thread_reader(stdout_pipe, stderr_pipe, finished):
    while not finished.is_set():
        stdout = stdout_pipe.read()
        stderr = stderr_pipe.read()
        if stdout: 
            global THREAD_STDOUT
            THREAD_STDOUT += stdout
        if stderr:
            global THREAD_STDERR
            THREAD_STDERR += stderr
        time.sleep(THREAD_SLEEP)

def run_command_and_get_output(command):
    # note: this does not properly output the results from sub processes opened
    stderr = b""
    stdout = b""
    rc = 0

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    
    # note: this pollutes stdout with both stdout and stderr    
    # while True:
    #     if proc.poll() is not None:
    #         break
    #     stdout += proc.stdout.read()
    #     stderr += proc.stderr.read()

    reader_finished = threading.Event()
    reader_thread = threading.Thread(target=thread_reader, args=(proc.stdout, proc.stderr, reader_finished))
    reader_thread.start()
    proc.wait()
    reader_finished.set()
    reader_thread.join()

    stdout = THREAD_STDOUT
    stderr = THREAD_STDERR

    # try:
    #     stdout, stderr = proc.communicate(timeout=15)
    #     while True:
    #         if process.poll() is not None:
    #             break
    #         data = process.stdout.readline()
    #         print data
    # except TimeoutExpired:
    #     proc.kill()
    #     stdout, stderr = proc.communicate()

    rc = proc.returncode

    return stdout.decode(ENCODING), stderr.decode(ENCODING), rc

class TestDuplicateFinder(unittest.TestCase):

    def setUp(self):
        print("Creating test folder: [{}]".format(TEST_FOLDER))
        os.mkdir(TEST_FOLDER)

    def tearDown(self):
        print("Deleting folder recursively: [{}]".format(TEST_FOLDER))
        shutil.rmtree(TEST_FOLDER)

    def test_single_file(self):
        # os.system(SCRIPT + " " + TEST_FOLDER) # todo: remove console print pollution from running tests
        stdout, stderr, rc = run_command_and_get_output(SCRIPT + " " + TEST_FOLDER)
        print(stdout)
        pass

    def test_two_files_non_duplicate(self):
        pass

    def test_two_files_duplicated(self):
        pass

if __name__ == "__main__":
    #print(FOLDER)
    #print(os.path.join(FOLDER, SUB_FOLDER))
    unittest.main()