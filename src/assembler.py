
import argparse
import sys

from parser import parse_program


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


def main():
    parser = argparse.ArgumentParser(
        description="Ассемблер учебной виртуальной машины, вариант №9"
    )

    parser.add_argument(
        "input",
        help="Путь к исходному YAML-файлу"
    )

    parser.add_argument(
        "output",
        help="Путь к выходному бинарному файлу (используется на этапе 2)"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Режим тестирования: вывести промежуточное представление"
    )

    args = parser.parse_args()

    try:
        program = parse_program(args.input)

        if args.test:
            print_internal_representation(program)
        else:
            print("Ассемблирование выполнено успешно.")
            print(f"Обработано команд: {len(program)}")
            print("Промежуточное представление создано.")
            print(
                "Формирование бинарного файла будет реализовано на этапе 2."
            )
            print(f"Путь для выходного файла: {args.output}")

    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
