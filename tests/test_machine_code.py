
import unittest

from src.parser import parse_program
from src.encoder import encode_program

from pathlib import Path


class TestMachineCode(unittest.TestCase):

    def setUp(self):
        self.test_file = (
            Path(__file__).parent / "variant9.yaml"
        )

        self.program = parse_program(self.test_file)

    def test_load_const(self):
        result = encode_program([self.program[0]])

        expected = bytes([
            0x03, 0x38, 0xA0, 0x00
        ])

        self.assertEqual(result, expected)

    def test_read_memory(self):
        result = encode_program([self.program[1]])

        expected = bytes([
            0x5C, 0x18, 0xEA, 0x00
        ])

        self.assertEqual(result, expected)

    def test_write_memory(self):
        result = encode_program([self.program[2]])

        expected = bytes([
            0x9E, 0x26, 0x00,
            0x00, 0x30, 0x02
        ])

        self.assertEqual(result, expected)

    def test_bswap(self):
        result = encode_program([self.program[3]])

        expected = bytes([
            0xF6, 0x81, 0x06,
            0x00, 0x00, 0x00
        ])

        self.assertEqual(result, expected)

    def test_complete_program(self):
        result = encode_program(self.program)

        expected = bytes([
            0x03, 0x38, 0xA0, 0x00,
            0x5C, 0x18, 0xEA, 0x00,
            0x9E, 0x26, 0x00,
            0x00, 0x30, 0x02,
            0xF6, 0x81, 0x06,
            0x00, 0x00, 0x00
        ])

        self.assertEqual(result, expected)

    def test_program_size(self):
        result = encode_program(self.program)

        self.assertEqual(len(result), 20)


if __name__ == "__main__":
    unittest.main()
