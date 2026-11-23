
import unittest
import tempfile
import csv

from pathlib import Path

from src.parser import parse_program
from src.encoder import encode_program
from src.interpreter import Interpreter


class TestInterpreter(unittest.TestCase):

    def setUp(self):
        self.copy_file = (
            Path(__file__).parent / "copy_array.yaml"
        )

        self.initial_data = {
            100: 11,
            101: 22,
            102: 33,
        }

        program = parse_program(self.copy_file)
        machine_code = encode_program(program)

        self.interpreter = Interpreter(
            machine_code,
            self.initial_data
        )

    def test_load_const(self):
        program = parse_program(self.copy_file)
        machine_code = encode_program([program[0]])

        interpreter = Interpreter(machine_code)
        interpreter.run()

        self.assertEqual(
            interpreter.memory.read_register(1),
            100
        )

    def test_read_memory(self):
        program = parse_program(self.copy_file)
        machine_code = encode_program(program[:2])

        interpreter = Interpreter(
            machine_code,
            self.initial_data
        )

        interpreter.run()

        self.assertEqual(
            interpreter.memory.read_register(2),
            11
        )

    def test_write_memory(self):
        program = parse_program(self.copy_file)
        machine_code = encode_program(program[:3])

        interpreter = Interpreter(
            machine_code,
            self.initial_data
        )

        interpreter.run()

        self.assertEqual(
            interpreter.memory.read_data(200),
            11
        )

    def test_copy_array(self):
        self.interpreter.run()

        self.assertEqual(
            self.interpreter.memory.read_data(200),
            11
        )

        self.assertEqual(
            self.interpreter.memory.read_data(201),
            22
        )

        self.assertEqual(
            self.interpreter.memory.read_data(202),
            33
        )

    def test_executed_commands(self):
        self.interpreter.run()

        self.assertEqual(
            self.interpreter.executed_commands,
            7
        )

    def test_csv_dump(self):
        self.interpreter.run()

        with tempfile.TemporaryDirectory() as directory:
            dump_path = Path(directory) / "dump.csv"

            self.interpreter.save_dump(
                dump_path,
                200,
                202
            )

            with open(
                dump_path,
                "r",
                newline="",
                encoding="utf-8"
            ) as file:
                rows = list(csv.DictReader(file))

            expected = [
                {"address": "200", "value": "11"},
                {"address": "201", "value": "22"},
                {"address": "202", "value": "33"},
            ]

            self.assertEqual(rows, expected)


if __name__ == "__main__":
    unittest.main()
