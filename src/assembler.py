
import argparse
import sys

from parser import parse_program
from encoder import save_binary, encode_program


def print_internal_representation(program):
    """Выводит промежуточное представление программы."""

    print("\nПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ПРОГРАММЫ")
    print("=" * 45)

    for index, instruction in enumerate(program, start=1):
        print(f"\nКоманда №{index}: {instruction['command']}")

        for field, value in instruction.items():
            if field == "command":
                continue

            print(f"  {field} = {value}")

    print("\n" + "=" * 45)
    print(f"Всего команд: {len(program)}")


def print_machine_code(machine_code):
    """Выводит машинный код в шестнадцатеричном формате."""

    print("\nМАШИННЫЙ КОД")
    print("=" * 45)

    position = 0

    while position < len(machine_code):
        opcode = machine_code[position] & 0x0F

        if opcode in (3, 12):
            size = 4
        else:
            size = 6

        instruction_bytes = machine_code[position:position + size]

        print(
            ", ".join(
                f"0x{byte:02X}" for byte in instruction_bytes
            )
        )

        position += size

    print("=" * 45)


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Ассемблер учебной виртуальной машины, вариант №9"
    )

    parser.add_argument(
        "input",
        help="Путь к исходному YAML-файлу"
    )

    parser.add_argument(
        "output",
        help="Путь к выходному бинарному файлу"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Режим тестирования"
    )

    return parser.parse_args()


def main():
    """Запускает программу из командной строки."""
    args = parse_args()

    try:
        program = parse_program(args.input)

        machine_code = encode_program(program)

        file_size = save_binary(program, args.output)

        if args.test:
            print_internal_representation(program)
            print_machine_code(machine_code)

        print(f"\nРазмер двоичного файла: {file_size} байт")
        print(f"Файл сохранен: {args.output}")

    except (ValueError, OSError, KeyError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
