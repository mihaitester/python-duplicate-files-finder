import os
import shutil
import unittest

import subprocess
import threading
import time
import copy
import sys

import random

BASE_FOLDER = os.path.abspath(os.path.dirname(__file__))
TEST_FOLDER = os.path.join(BASE_FOLDER, "scrap_test_folder")
SCRIPT = "duplicate-finder.cmd"
SCRIPT_PARALELIZED = "duplicate-finder.cmd -p"
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
            try:
                print("Process reading thread failed with [{}]".format(ex.message))
            except:
                print("Process reading thread failed with [{}]".format(str(ex)))
            finished.set() # note: without this the thread loops indefinetely


def run_command_and_get_output(command):
    # note: this does not properly output the results from sub processes opened, makes me think that python is hacked and that processes are virtualized instead of actually running in their own shell
    stderr = ""
    stdout = ""
    rc = 0

    # print("{}".format(command))

    # note: this fixes handles but it does not return the full output from process # todo: figure out why this fails [ ResourceWarning: Enable tracemalloc to get the object allocation traceback ]
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
            proc.wait() # bug: its highly probable that this hangs the scripts -> running tests for parallelized threads hangs this test script
            reader_finished.set()
            reader_thread.join()
        except Exception as ex:
            try:
                print("Failed to start process reading thread with [{}]".format(ex.message))
            except:
                print("Failed to start process reading thread with [{}]".format(str(ex)))
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


class TestDuplicateFinder_SingleThread(unittest.TestCase):

    prefix = "---"

    def setUp(self):
        # print("Creating test folder: [{}]".format(TEST_FOLDER))
        os.mkdir(TEST_FOLDER)

    def tearDown(self):
        # print("Deleting folder recursively: [{}]".format(TEST_FOLDER))
        shutil.rmtree(TEST_FOLDER)

    def test_no_file(self): 
        print(self.prefix + self.id())
        # os.system(SCRIPT + " " + TEST_FOLDER) # todo: remove console print pollution from running tests
        stdout, stderr, rc = run_command_and_get_output(SCRIPT + " " + TEST_FOLDER)
        # print(stdout)
        print(stderr)
        self.assertTrue("Found [0] duplicated files" in stderr)
        # print(stderr) # todo: understand why logging is happening on STDERR channel and not STDOUT channel
        # print(rc)
    
    def test_single_file(self):
        print(self.prefix + self.id())
        with open(os.path.join(TEST_FOLDER, "test1.txt"), "w") as writefile:
            writefile.write("Something not useful")
        stdout, stderr, rc = run_command_and_get_output(SCRIPT + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [0] duplicated files" in stderr)

    def test_2_files_non_duplicate(self):
        print(self.prefix + self.id())
        with open(os.path.join(TEST_FOLDER, "test1.txt"), "w") as writefile:
            writefile.write("Something not useful")
        with open(os.path.join(TEST_FOLDER, "test2.txt"), "w") as writefile:
            writefile.write("Something not useful but different")
        stdout, stderr, rc = run_command_and_get_output(SCRIPT + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [0] duplicated files" in stderr)

    def test_2_files_duplicated(self):
        print(self.prefix + self.id())
        content = "Something not useful"
        with open(os.path.join(TEST_FOLDER, "test1.txt"), "w") as writefile:
            writefile.write(content)
        with open(os.path.join(TEST_FOLDER, "test2.txt"), "w") as writefile:
            writefile.write(content)
        stdout, stderr, rc = run_command_and_get_output(SCRIPT + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [1] duplicated files" in stderr)

    def test_100_files_non_duplicate(self):
        print(self.prefix + self.id())
        content = "Something not useful"
        for i in range(0,100):
            with open(os.path.join(TEST_FOLDER, "test"+str(i)+".txt"), "w") as writefile:
                writefile.write(content + str(i))
        stdout, stderr, rc = run_command_and_get_output(SCRIPT + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [0] duplicated files" in stderr)

    def test_100_files_all_duplicate(self):
        print(self.prefix + self.id())
        content = "Something not useful"
        duplicates = 100
        for i in range(0,duplicates):
            with open(os.path.join(TEST_FOLDER, "test"+str(i)+".txt"), "w") as writefile:
                writefile.write(content)
        stdout, stderr, rc = run_command_and_get_output(SCRIPT + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [" + str(duplicates) + "] duplicated files" in stderr)

    def test_100_files_random_duplicate(self):
        print(self.prefix + self.id())
        content = "Something not useful"
        duplicates = random.randint(0, 100)
        duplicated = 0
        for i in range(0,100):
            with open(os.path.join(TEST_FOLDER, "test"+str(i)+".txt"), "w") as writefile:
                if duplicated < duplicates:
                    writefile.write(content)
                    duplicated += 1
                else:
                    writefile.write(content + str(i))
        stdout, stderr, rc = run_command_and_get_output(SCRIPT + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found ["+str(duplicates)+"] duplicated files" in stderr)


class TestDuplicateFinder_Paralelized(unittest.TestCase):
    # note: unittest uses exceptions to communicate test results, hence if the subthreads fail, that can interfere with results -> help: [ https://stackoverflow.com/questions/40447290/python-unittest-and-multithreading ]

    prefix = "==="

    def setUp(self):
        # print("Creating test folder: [{}]".format(TEST_FOLDER))
        os.mkdir(TEST_FOLDER)

    def tearDown(self):
        # print("Deleting folder recursively: [{}]".format(TEST_FOLDER))
        shutil.rmtree(TEST_FOLDER)

    def test_no_file(self):
        print(self.prefix + self.id())
        # os.system(SCRIPT_PARALELIZED + " " + TEST_FOLDER) # todo: remove console print pollution from running tests
        stdout, stderr, rc = run_command_and_get_output(SCRIPT_PARALELIZED + " " + TEST_FOLDER)
        # print(stdout)
        self.assertTrue("Found [0] duplicated files" in stderr)
        # print(stderr) # todo: understand why logging is happening on STDERR channel and not STDOUT channel
        # print(rc)

    def test_single_file(self):
        print(self.prefix + self.id())
        with open(os.path.join(TEST_FOLDER, "test1.txt"), "w") as writefile:
            writefile.write("Something not useful")
        stdout, stderr, rc = run_command_and_get_output(SCRIPT_PARALELIZED + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [0] duplicated files" in stderr)

    def test_2_files_non_duplicate(self):
        print(self.prefix + self.id())
        with open(os.path.join(TEST_FOLDER, "test1.txt"), "w") as writefile:
            writefile.write("Something not useful")
        with open(os.path.join(TEST_FOLDER, "test2.txt"), "w") as writefile:
            writefile.write("Something not useful but different")
        stdout, stderr, rc = run_command_and_get_output(SCRIPT_PARALELIZED + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [0] duplicated files" in stderr)

    def test_2_files_duplicated(self):
        print(self.prefix + self.id())
        content = "Something not useful"
        with open(os.path.join(TEST_FOLDER, "test1.txt"), "w") as writefile:
            writefile.write(content)
        with open(os.path.join(TEST_FOLDER, "test2.txt"), "w") as writefile:
            writefile.write(content)
        stdout, stderr, rc = run_command_and_get_output(SCRIPT_PARALELIZED + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [1] duplicated files" in stderr)

    def test_100_files_non_duplicate(self):
        print(self.prefix + self.id())
        content = "Something not useful"
        for i in range(0,100):
            with open(os.path.join(TEST_FOLDER, "test"+str(i)+".txt"), "w") as writefile:
                writefile.write(content + str(i))
        stdout, stderr, rc = run_command_and_get_output(SCRIPT_PARALELIZED + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [0] duplicated files" in stderr)

    def test_100_files_all_duplicate(self):
        print(self.prefix + self.id())
        content = "Something not useful"
        duplicates = 100
        for i in range(0,duplicates):
            with open(os.path.join(TEST_FOLDER, "test"+str(i)+".txt"), "w") as writefile:
                writefile.write(content)
        stdout, stderr, rc = run_command_and_get_output(SCRIPT_PARALELIZED + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found [" + str(duplicates) + "] duplicated files" in stderr)

    def test_100_files_random_duplicate(self):
        print(self.prefix + self.id())
        content = "Something not useful"
        duplicates = random.randint(0, 100)
        duplicated = 0
        for i in range(0,100):
            with open(os.path.join(TEST_FOLDER, "test"+str(i)+".txt"), "w") as writefile:
                if duplicated < duplicates:
                    writefile.write(content)
                    duplicated += 1
                else:
                    writefile.write(content + str(i))
        stdout, stderr, rc = run_command_and_get_output(SCRIPT_PARALELIZED + " " + TEST_FOLDER)
        print(stderr)
        self.assertTrue("Found ["+str(duplicates)+"] duplicated files" in stderr)


def main(verbosity=1):
    # note: really weird that verbosity cannot be passed through, but unittest will automatically process --verbose parameter from sys.argv
    unittest.main()

if __name__ == "__main__":
    #print(FOLDER)
    #print(os.path.join(FOLDER, SUB_FOLDER))
    # if len(sys.argv) > 1:
    #     print(sys.argv)
    #     # note: need to provide verbosity level [0,1,2 -> 2 is most verbose] -> help: [ https://stackoverflow.com/questions/1322575/what-numbers-can-you-pass-as-verbosity-in-running-python-unit-test-suites ]
    #     main(int(sys.argv[1])) 
    # else:
    #     main()
    main()
    # todo: maybe add a logger for tests as well