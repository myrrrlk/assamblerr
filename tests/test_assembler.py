
import unittest
from pathlib import Path

from src.parser import parse_program


class TestAssembler(unittest.TestCase):

    def setUp(self):
        self.test_file = (
            Path(__file__).parent / "variant9.yaml"
        )

    def test_all_commands(self):
        program = parse_program(self.test_file)

        expected = [
            {
                "command": "load_const",
                "A": 3,
                "B": 896,
                "C": 5,
            },
            {
                "command": "read_memory",
                "A": 12,
                "B": 389,
                "C": 42,
                "D": 3,
            },
            {
                "command": "write_memory",
                "A": 14,
                "B": 617,
                "C": 35,
            },
            {
                "command": "bswap",
                "A": 6,
                "B": 31,
                "C": 416,
            },
        ]

        self.assertEqual(program, expected)

    def test_number_of_commands(self):
        program = parse_program(self.test_file)

        self.assertEqual(len(program), 4)

    def test_command_opcodes(self):
        program = parse_program(self.test_file)

        opcodes = [instruction["A"] for instruction in program]

        self.assertEqual(opcodes, [3, 12, 14, 6])


if __name__ == "__main__":
    unittest.main()
