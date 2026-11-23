
import unittest
from pathlib import Path

from src.parser import parse_program
from src.encoder import encode_program
from src.interpreter import Interpreter


class TestBswap(unittest.TestCase):

    def setUp(self):
        self.test_file = (
            Path(__file__).parent / "bswap.yaml"
        )

        program = parse_program(self.test_file)
        machine_code = encode_program(program)

        self.interpreter = Interpreter(machine_code)

    def test_bswap_result(self):
        self.interpreter.run()

        result = self.interpreter.memory.read_data(416)

        self.assertEqual(result, 0x45230100)

    def test_source_register(self):
        self.interpreter.run()

        result = self.interpreter.memory.read_register(31)

        self.assertEqual(result, 74565)

    def test_bswap_command_count(self):
        self.interpreter.run()

        self.assertEqual(
            self.interpreter.executed_commands,
            2
        )

    def test_bswap_result_bytes(self):
        self.interpreter.run()

        result = self.interpreter.memory.read_data(416)

        expected = bytes([0x45, 0x23, 0x01, 0x00])

        actual = result.to_bytes(4, byteorder="big")

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
