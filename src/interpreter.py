
import argparse
import csv
import sys


class Memory:
    """Модель памяти виртуальной машины."""

    def __init__(self):
        # Память команд.
        self.instruction_memory = b""

        # 64 регистра.
        self.registers = [0] * 64

        # Память данных.
        self.data_memory = {}

    def load_program(self, program):
        self.instruction_memory = program

    def read_register(self, address):
        if not 0 <= address < 64:
            raise ValueError(
                f"Недопустимый адрес регистра: {address}"
            )

        return self.registers[address]

    def write_register(self, address, value):
        if not 0 <= address < 64:
            raise ValueError(
                f"Недопустимый адрес регистра: {address}"
            )

        self.registers[address] = value

    def read_data(self, address):
        if address < 0:
            raise ValueError("Адрес памяти не может быть отрицательным.")

        return self.data_memory.get(address, 0)

    def write_data(self, address, value):
        if address < 0:
            raise ValueError("Адрес памяти не может быть отрицательным.")

        self.data_memory[address] = value


class Interpreter:
    """Интерпретатор виртуальной машины, вариант №9."""

    COMMAND_SIZES = {
        3: 4,
        12: 4,
        14: 6,
        6: 6,
    }

    def __init__(self, program, initial_data=None):
        self.memory = Memory()
        self.memory.load_program(program)

        if initial_data:
            for address, value in initial_data.items():
                self.memory.write_data(address, value)

        self.pc = 0
        self.executed_commands = 0

    def decode_instruction(self):
        """Декодирование машинной команды."""

        program = self.memory.instruction_memory

        if self.pc >= len(program):
            return None

        first_byte = program[self.pc]
        opcode = first_byte & 0x0F

        if opcode not in self.COMMAND_SIZES:
            raise ValueError(
                f"Неизвестная команда: {opcode}, адрес: {self.pc}"
            )

        size = self.COMMAND_SIZES[opcode]

        instruction_bytes = program[
            self.pc:self.pc + size
        ]

        if len(instruction_bytes) != size:
            raise ValueError(
                f"Недостаточно байтов для команды по адресу {self.pc}"
            )

        value = int.from_bytes(
            instruction_bytes,
            byteorder="little"
        )

        instruction = {
            "A": opcode,
            "size": size,
        }

        # load_const
        if opcode == 3:
            instruction["B"] = (value >> 4) & 0x1FFFF
            instruction["C"] = (value >> 21) & 0x3F

        # read_memory
        elif opcode == 12:
            instruction["B"] = (value >> 4) & 0xFFF
            instruction["C"] = (value >> 16) & 0x3F
            instruction["D"] = (value >> 22) & 0x3F

        # write_memory
        elif opcode == 14:
            instruction["B"] = (value >> 4) & 0xFFFFFFFF
            instruction["C"] = (value >> 36) & 0x3F

        # bswap
        elif opcode == 6:
            instruction["B"] = (value >> 4) & 0x3F
            instruction["C"] = (value >> 10) & 0xFFFFFFFF

        return instruction

    def execute_instruction(self, instruction):
        """Выполнение машинной команды."""

        opcode = instruction["A"]

        # 1. Загрузка константы.
        if opcode == 3:
            constant = instruction["B"]
            destination = instruction["C"]

            self.memory.write_register(
                destination,
                constant
            )

        # 2. Чтение из памяти.
        elif opcode == 12:
            offset = instruction["B"]
            destination = instruction["C"]
            base_register = instruction["D"]

            base_address = self.memory.read_register(
                base_register
            )

            address = base_address + offset

            value = self.memory.read_data(address)

            self.memory.write_register(
                destination,
                value
            )

        # 3. Запись в память.
        elif opcode == 14:
            address = instruction["B"]
            source_register = instruction["C"]

            value = self.memory.read_register(
                source_register
            )

            self.memory.write_data(
                address,
                value
            )

        # 4. Изменение порядка байтов.
        elif opcode == 6:
            source_register = instruction["B"]
            destination_address = instruction["C"]

            value = self.memory.read_register(
                source_register
            )

            if not 0 <= value <= 0xFFFFFFFF:
                raise ValueError(
                    "Значение bswap должно помещаться в 32 бита."
                )

            result = int.from_bytes(
                value.to_bytes(4, byteorder="little"),
                byteorder="big"
            )

            self.memory.write_data(
                destination_address,
                result
            )

        else:
            raise ValueError(
                f"Неизвестная операция: {opcode}"
            )

    def run(self):
        """Основной цикл интерпретации."""

        while self.pc < len(self.memory.instruction_memory):

            instruction = self.decode_instruction()

            if instruction is None:
                break

            self.execute_instruction(instruction)

            self.pc += instruction["size"]
            self.executed_commands += 1

        return self.memory

    def save_dump(self, output_path, start_address, end_address):
        """Сохранение дампа памяти в CSV."""

        if start_address < 0 or end_address < start_address:
            raise ValueError(
                "Некорректный диапазон адресов памяти."
            )

        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow(["address", "value"])

            for address in range(
                start_address,
                end_address + 1
            ):
                value = self.memory.read_data(address)

                writer.writerow([
                    address,
                    value
                ])


def load_initial_memory(file_path):
    """Загрузка начальной памяти из CSV."""

    initial_data = {}

    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV-файл пустой.")

        reader.fieldnames = [
            name.strip() for name in reader.fieldnames
        ]

        if reader.fieldnames != ["address", "value"]:
            raise ValueError(
                f"Неверные заголовки CSV: {reader.fieldnames}. "
                "Ожидаются address,value."
            )

        for row in reader:
            address = int(row["address"].strip(), 0)
            value = int(row["value"].strip(), 0)

            if address < 0:
                raise ValueError(
                    "Адрес памяти не может быть отрицательным."
                )

            initial_data[address] = value

    return initial_data


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Интерпретатор учебной виртуальной машины, вариант №9"
        )
    )

    parser.add_argument(
        "input",
        help="Путь к бинарному файлу"
    )

    parser.add_argument(
        "dump",
        help="Путь к CSV-дампу"
    )

    parser.add_argument(
        "start",
        type=int,
        help="Начальный адрес памяти"
    )

    parser.add_argument(
        "end",
        type=int,
        help="Конечный адрес памяти"
    )

    parser.add_argument(
        "--init",
        help="Файл с начальными данными памяти"
    )

    args = parser.parse_args()

    try:
        with open(args.input, "rb") as file:
            program = file.read()

        initial_data = {}

        if args.init:
            initial_data = load_initial_memory(args.init)

        interpreter = Interpreter(
            program,
            initial_data
        )

        interpreter.run()

        interpreter.save_dump(
            args.dump,
            args.start,
            args.end
        )

        print("Выполнение программы завершено.")
        print(
            f"Выполнено команд: {interpreter.executed_commands}"
        )
        print(f"Дамп памяти сохранен: {args.dump}")
        print(
            f"Диапазон памяти: {args.start} - {args.end}"
        )

    except (
        ValueError,
        OSError,
        NotImplementedError
    ) as error:

        print(
            f"Ошибка: {error}",
            file=sys.stderr
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
