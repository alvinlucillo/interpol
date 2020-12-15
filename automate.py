import subprocess
import pathlib
import os

script = "ab-lucillo-03.py"


def main():

    testcase = ["testcase\\tc1.ipol", "testcase\\tc2.ipol", "testcase\\tc3.ipol", "testcase\\tc4.ipol",
                "testcase\\tc5_invalidfile.txt", "testcase\\tc6.ipol", "testcase\\tc7.ipol",
                "\\testcase\\tc8_invalid_file.txt",
                "C:\\Users\\alvin.lucillo\\PycharmProjects\\interpol\\testcase\\tc9_absolute_path.ipol"]
    testdata = [[], [], ["12\n"], ["1986\n"], [], [], [], [], []]
    desc = ["In Specs", "In Specs", "In Specs", "In Specs", "In Specs", "File not found", "Empty file", "Invalid file",
            "Absolute path"]

    tc = 0
    successful = 0
    for tcase in testcase:
        tc = tc + 1
        if run_test(tcase, tc, desc[tc-1], testdata[tc-1], True, False, True):
            successful = successful + 1

    print("\n#####################################\nSuccessful cases over total cases: " + str(successful) + "/" +
          str(tc) + "\n#####################################")


def run_test(tc, tc_no, desc, input_data=None, show_result=False, formatted=False, show_difference=False):

    file_path = pathlib.Path(str(pathlib.Path(__file__).parent.absolute()), script)
    process = subprocess.Popen(["python", file_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    src = tc + "\n"
    process.stdin.write(str.encode(src))

    if input_data is not None and len(input_data) > 0:
        for data in input_data:
            process.stdin.write(str.encode(data))

    output = process.communicate()[0].decode()

    process.stdin.close()

    file_name = "testcase\\tc" + str(tc_no) + "_result.txt"
    file_path = pathlib.Path(str(pathlib.Path(__file__).parent.absolute()), file_name)

    file = open(file_path, 'r')
    expected = file.read()
    repr_expected = repr(expected)
    repr_result = str(repr(output)).replace("\\r", "")

    print("\n************\nTEST CASE #" + str(tc_no) + " - " + desc + "\n************")

    successful = repr_expected == repr_result

    if show_result and not successful:
        result = str(repr(output)).replace("\\r", "")
        expected_result = repr(expected)

        if formatted:
            result = output
            expected_result = expected

        print("Output: \n" + result)
        print("Expected: \n" + expected_result)

    print("\nSUCCESSFUL: " + str(successful))

    return successful


main()
