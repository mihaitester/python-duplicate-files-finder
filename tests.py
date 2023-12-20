import os
import shutil
import unittest

import subprocess
import threading
import time
import copy

BASE_FOLDER = os.path.abspath(os.path.dirname(__file__))
TEST_FOLDER = os.path.join(BASE_FOLDER, "scrap_test_folder")
SCRIPT = "duplicate-finder.cmd"
ENCODING = "UTF-8"

# THREAD_LOCK = threading.Lock() # note: this is not needed because there is a single reading thread, and the tests are sequential and processes launched are being waited for
THREAD_STDOUT = b""
THREAD_STDERR = b""
THREAD_SLEEP = 2

def thread_reader(stdout_pipe, stderr_pipe, finished):
    
    global THREAD_STDOUT, THREAD_STDERR
    THREAD_STDOUT = b""
    THREAD_STDERR = b""
    
    while not finished.is_set():
        time.sleep(THREAD_SLEEP)
        try:
            stdout = stdout_pipe.read()
            stderr = stderr_pipe.read()
            if stdout:
                # THREAD_LOCK.acquire()
                THREAD_STDOUT = THREAD_STDOUT + stdout
                # THREAD_LOCK.release()
                # print(stdout)
                # print(THREAD_STDOUT)
            if stderr:
                # THREAD_LOCK.acquire()
                THREAD_STDERR = THREAD_STDERR + stderr
                # THREAD_LOCK.release()
                # print(stderr)
                # print(THREAD_STDERR)
        except Exception as ex:
            print("Process reading thread failed with [{}]".format(ex.message))


def run_command_and_get_output(command):
    # note: this does not properly output the results from sub processes opened, makes me think that python is hacked and that processes are virtualized instead of actually running in their own shell
    stderr = ""
    stdout = ""
    rc = 0

    # note: this fixes handles but it does not return the full output from process
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        # note: this pollutes stdout with both stdout and stderr    
        # while True:
        #     if proc.poll() is not None:
        #         break
        #     stdout += proc.stdout.read()
        #     stderr += proc.stderr.read()
        try:
            reader_finished = threading.Event()
            reader_thread = threading.Thread(target=thread_reader, args=(proc.stdout, proc.stderr, reader_finished))
            reader_thread.start()
            proc.wait()
            reader_finished.set()
            reader_thread.join()
        except Exception as ex:
            print("Failed to start process reading thread with [{}]".format(ex.message))
        # proc.kill()

        # THREAD_LOCK.acquire()
        stdout = THREAD_STDOUT.decode(ENCODING)
        stderr = THREAD_STDERR.decode(ENCODING)
        rc = proc.returncode
        # THREAD_LOCK.release()
        
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
    
    # note: these work, but outside this global method, the test class fails to be used properly
    # print(stdout)
    # print(stderr)
    # print(rc)
    return stdout, stderr, rc


class TestDuplicateFinder(unittest.TestCase):

    def setUp(self):
        print("Creating test folder: [{}]".format(TEST_FOLDER))
        os.mkdir(TEST_FOLDER)

    def tearDown(self):
        print("Deleting folder recursively: [{}]".format(TEST_FOLDER))
        shutil.rmtree(TEST_FOLDER)

    def test_single_file(self):
        # os.system(SCRIPT + " " + TEST_FOLDER) # todo: remove console print pollution from running tests
        stdout, stderr, rc = run_command_and_get_output(SCRIPT + " " + TEST_FOLDER) # todo: figure out why this fails [ ResourceWarning: Enable tracemalloc to get the object allocation traceback ]
        # print(stdout)
        print(stderr) # todo: understand why logging is happening on STDERR channel and not STDOUT channel
        # print(rc)
        pass

    # def test_two_files_non_duplicate(self):
        # pass

    # def test_two_files_duplicated(self):
        # pass

if __name__ == "__main__":
    #print(FOLDER)
    #print(os.path.join(FOLDER, SUB_FOLDER))
    unittest.main()