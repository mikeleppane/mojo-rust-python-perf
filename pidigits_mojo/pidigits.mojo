from python import Python, PythonObject
from benchmark import run, keep
import time

fn benchmark(digits: Int32) raises:
    Python.add_to_path("/home/mikko/dev/python-rust-mojo-perf/python_rust_mojo_perf/pidigits")
    var pidigits = Python.import_module("pidigits")

    var start = time.now()
    var res: String = pidigits.chudnovsky(digits)

    var end = time.now()

    print(res[0])
    var elapsed = (end - start)/1e6
    print("Elapsed time: ")
    print(elapsed)


fn main() raises:
    benchmark(10000)