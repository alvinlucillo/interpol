import subprocess
from subprocess import Popen, PIPE, STDOUT
import os
import pathlib
import difflib


def main():

    run_test(2, ["hello world\n"], True, False, True)


def run_test(tc, input_data, show_result=False, formatted=False, show_difference=False):
    process = subprocess.Popen(["python", "ab-lucillo-03.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    src = "testcase\\tc" + str(tc) + ".ipol\n"
    process.stdin.write(str.encode(src))
    process.stdin.write(str.encode(input_data[0]))

    output = process.communicate()[0].decode()

    process.stdin.close()

    file_name = "testcase/tc" + str(tc) + "_result.txt"
    file_path = pathlib.Path(str(pathlib.Path(__file__).parent.absolute()), file_name)

    file = open(file_path, 'r')
    expected = file.read()

    print("************\nTEST CASE #" + str(tc))

    result = str(repr(output)).replace("\\r", "")

    if show_result:
        expected_result = repr(expected)

        if formatted:
            result = output
            expected_result = expected

        print("Output: \n" + result)
        print("Expected: \n" + expected_result)

    successful = repr(expected) == result

    if show_difference:
        diff = difflib.Differ().compare(repr(expected), result)
        for d in diff:
            print(d, end="")

    print("\nSUCCESSFUL: " + str(successful))

def tst():
    child = subprocess.Popen(['python', 'automate1.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    child.stdin.write(str.encode("hello\n"))
    child.stdin.write(str.encode("world"))
    print(child.communicate()[0].decode())


    child.stdin.close()


main()
