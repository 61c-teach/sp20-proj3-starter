#!/usr/bin/env python3

import os
import os.path
import tempfile
import subprocess
import signal
import re
import sys

script_dir = os.path.realpath(sys.path[0])
logisim_location = os.path.join(script_dir, "../../../logisim-evolution.jar")

tests = [
  ("ALU add test", "alu-add"),
  ("ALU div and rem test", "alu-div-rem"),
  ("ALU mulh test (extra credit)", "alu-mulh"),
  ("ALU mult/mulhu test", "alu-mult"),
  ("ALU slt, sub, BSel test", "alu-slt-sub-bsel"),
  ("ALU shift test", "alu-shift"),

  ("ALU logic test", "alu-logic"),

  ("ALU comprehensive test", "alu-comprehensive"),
]

class LogisimTest():
  """
  Runs a circuit file and compares output against the provided reference file.
  """

  def __init__(self, circ_path, trace_path):
    self.circ_path  = circ_path
    self.trace_path = trace_path

  def __call__(self, filename):
    output = tempfile.TemporaryFile(mode="r+")
    try:
      stdinf = open("/dev/null")
    except Exception as e:
      try:
        stdinf = open("nul")
      except Exception as e:
         print("Could not open nul or /dev/null. Program will most likely error now.")
    proc = subprocess.Popen(["java", "-jar", logisim_location, "-tty", "table", self.circ_path],
                            cwd=script_dir, stdin=stdinf, stdout=subprocess.PIPE)
    try:
      reference = open(self.trace_path)
      passed = compare_unbounded(proc.stdout, reference, filename)
    finally:
      try:
        os.kill(proc.pid, signal.SIGTERM)
      except Exception as e:
        pass
    if passed:
      return (True, "Matched expected output")
    else:
      return (False, "Did not match expected output")

def compare_unbounded(student_out, reference_out, filename):
  passed = True
  student_output_array = []
  while True:
    line1 = student_out.readline().rstrip().decode("utf-8", "namereplace")
    line2 = reference_out.readline().rstrip()
    if line2 == "":
      break
    student_output_array.append(line1)
    m = re.match(line2, line1)
    if m == None or m.start() != 0 or m.end() != len(line2):
      passed = False
  with open(filename, "w") as student_output:
    for line in student_output_array:
      student_output.write(line + "\n")
  return passed

def run_test(test_slug, output_type=None):
  output_slug = test_slug
  if output_type:
    output_slug += "-" + output_type
  circ_path = os.path.join(script_dir, "%s.circ" % test_slug)
  reference_output_path = os.path.join(script_dir, "reference_output/%s-ref.out" % output_slug)
  student_output_path = os.path.join(script_dir, "student_output/%s-student.out" % output_slug)
  test_runner = LogisimTest(circ_path, reference_output_path)
  return test_runner(student_output_path)

def run_tests(tests):
  print("Testing files...")
  tests_passed = 0
  tests_failed = 0

  for test in tests:
    description, test_slug = test[:2]
    output_type = (test[2] if len(test) >= 3 else "")
    did_pass, fail_reason = False, "Unknown test error"
    try:
      did_pass, fail_reason = run_test(test_slug, output_type)
    except Exception as ex:
      print(ex)
    if did_pass:
      print("\tPASSED test: %s" % description)
      tests_passed += 1
    else:
      print("\tFAILED test: %s (%s)" % (description, fail_reason))
      tests_failed += 1

  print("Passed %d/%d tests" % (tests_passed, (tests_passed + tests_failed)))

if __name__ == "__main__":
  run_tests(tests)
