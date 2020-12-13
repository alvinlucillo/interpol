import subprocess
import pathlib


def main():

    testdata = [[], ["hello world\n"]]

    tc = 0
    successful = 0
    for data in testdata:
        tc = tc + 1
        if run_test(tc, data, True, True, True):
            successful = successful + 1

    print("\n#####################################\nSuccesful cases over total cases: " + str(successful) + "/" +
          str(tc) + "\n#####################################")


def run_test(tc, input_data=None, show_result=False, formatted=False, show_difference=False):
    process = subprocess.Popen(["python", "ab-lucillo-03.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    src = "testcase\\tc" + str(tc) + ".ipol\n"
    process.stdin.write(str.encode(src))

    if input_data is not None and len(input_data) > 0:
        for data in input_data:
            process.stdin.write(str.encode(data))

    output = process.communicate()[0].decode()

    process.stdin.close()

    file_name = "testcase/tc" + str(tc) + "_result.txt"
    file_path = pathlib.Path(str(pathlib.Path(__file__).parent.absolute()), file_name)

    file = open(file_path, 'r')
    expected = file.read()
    repr_expected = repr(expected
                         )
    print("\n************\nTEST CASE #" + str(tc) + "\n************")
    repr_result = str(repr(output)).replace("\\r", "")

    successful = repr_expected == repr_result

    if show_result and not successful:
        result = str(repr(output)).replace("\\r", "")
        expected_result = repr(expected)

        if formatted:
            result = output
            expected_result = expected

        print("Output: \n" + result)
        print("\nExpected: \n" + expected_result)

    if show_difference and not successful:
        ch_cnt = 0
        ch = ""
        ch1 = ""
        for c in repr_expected:
            ch = ch + c
            ch1 = ch1 + repr_result[ch_cnt]
            if c != repr_result[ch_cnt]:
                print("Difference detected. See last char.\nExpected " + ch + "\nResult:  " + ch1)
                break

            ch_cnt = ch_cnt + 1

    print("\nSUCCESSFUL: " + str(successful))

    return successful


def tst():
    child = subprocess.Popen(['python', 'automate1.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    child.stdin.write(str.encode("hello\n"))
    child.stdin.write(str.encode("world"))
    print(child.communicate()[0].decode())

    child.stdin.close()


main()
