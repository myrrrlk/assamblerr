
import unittest
from pathlib import Path

from src.parser import parse_program
from src.encoder import encode_program
from src.interpreter import Interpreter, load_initial_memory


class TestVector7(unittest.TestCase):

    def setUp(self):
        tests_dir = Path(__file__).parent

        program = parse_program(
            tests_dir / "vector7.yaml"
        )

        machine_code = encode_program(program)

        initial_data = load_initial_memory(
            tests_dir / "vector7_memory.csv"
        )

        self.interpreter = Interpreter(
            machine_code,
            initial_data
        )

    def test_vector_length(self):
        self.assertEqual(
            len(self.interpreter.memory.data_memory),
            7
        )

    def test_vector_bswap(self):
        self.interpreter.run()

        expected = [
            16777216,
            33554432,
            50331648,
            67108864,
            83886080,
            100663296,
            117440512
        ]

        actual = [
            self.interpreter.memory.read_data(address)
            for address in range(100, 107)
        ]

        self.assertEqual(actual, expected)

    def test_vector_in_place(self):
        self.interpreter.run()

        for address in range(100, 107):
            self.assertIn(
                address,
                self.interpreter.memory.data_memory
            )

    def test_command_count(self):
        self.interpreter.run()

        self.assertEqual(
            self.interpreter.executed_commands,
            15
        )


if __name__ == "__main__":
    unittest.main()
