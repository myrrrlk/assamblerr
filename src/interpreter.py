
import argparse
import csv
import sys


REGISTER_COUNT = 64
REGISTER_MASK = 0x3F
WORD_MASK = 0xFFFFFFFF
WORD_BYTES = 4
OPCODE_MASK = 0x0F
OPCODE_LOAD_CONST = 3
OPCODE_READ_MEMORY = 12
OPCODE_WRITE_MEMORY = 14
OPCODE_BSWAP = 6
SHORT_COMMAND_SIZE = 4
LONG_COMMAND_SIZE = 6


class Memory:
    """Модель памяти виртуальной машины."""

    def __init__(self):
        """Создаёт хранилища команд, регистров и данных."""
        self.instruction_memory = b""

        self.registers = [0] * REGISTER_COUNT

        self.data_memory = {}

    def load_program(self, program):
        """Загружает машинную программу."""
        self.instruction_memory = program

    def read_register(self, address):
        """Возвращает значение регистра."""
        if not 0 <= address < REGISTER_COUNT:
            raise ValueError(
                f"Недопустимый адрес регистра: {address}"
            )

        return self.registers[address]

    def write_register(self, address, value):
        """Записывает значение в регистр."""
        if not 0 <= address < REGISTER_COUNT:
            raise ValueError(
                f"Недопустимый адрес регистра: {address}"
            )

        self.registers[address] = value

    def read_data(self, address):
        """Читает значение из памяти данных."""
        if address < 0:
            raise ValueError("Адрес памяти не может быть отрицательным.")

        return self.data_memory.get(address, 0)

    def write_data(self, address, value):
        """Записывает значение в память данных."""
        if address < 0:
            raise ValueError("Адрес памяти не может быть отрицательным.")

        self.data_memory[address] = value


class Interpreter:
    """Интерпретатор виртуальной машины, вариант №9."""

    COMMAND_SIZES = {
        OPCODE_LOAD_CONST: SHORT_COMMAND_SIZE,
        OPCODE_READ_MEMORY: SHORT_COMMAND_SIZE,
        OPCODE_WRITE_MEMORY: LONG_COMMAND_SIZE,
        OPCODE_BSWAP: LONG_COMMAND_SIZE,
    }

    def __init__(self, program, initial_data=None):
        """Создаёт интерпретатор с начальным состоянием памяти."""
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
        opcode = first_byte & OPCODE_MASK

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

        instruction.update(self.decode_fields(opcode, value))
        return instruction

    @staticmethod
    def decode_fields(opcode, value):
        """Извлекает операнды из машинного кода."""
        fields = {
            OPCODE_LOAD_CONST: {"B": (4, 0x1FFFF), "C": (21, REGISTER_MASK)},
            OPCODE_READ_MEMORY: {"B": (4, 0xFFF), "C": (16, REGISTER_MASK),
                                 "D": (22, REGISTER_MASK)},
            OPCODE_WRITE_MEMORY: {"B": (4, WORD_MASK), "C": (36, REGISTER_MASK)},
            OPCODE_BSWAP: {"B": (4, REGISTER_MASK), "C": (10, WORD_MASK)},
        }
        return {field: (value >> shift) & mask
                for field, (shift, mask) in fields[opcode].items()}

    def execute_instruction(self, instruction):
        """Выбирает и выполняет операцию по её коду."""
        opcode = instruction["A"]
        handlers = {
            OPCODE_LOAD_CONST: self.execute_load_const,
            OPCODE_READ_MEMORY: self.execute_read_memory,
            OPCODE_WRITE_MEMORY: self.execute_write_memory,
            OPCODE_BSWAP: self.execute_bswap,
        }
        if opcode not in handlers:
            raise ValueError(f"Неизвестная операция: {opcode}")
        handlers[opcode](instruction)

    def execute_load_const(self, instruction):
        """Загружает константу в регистр."""
        self.memory.write_register(instruction["C"], instruction["B"])

    def execute_read_memory(self, instruction):
        """Читает данные по базовому адресу со смещением."""
        address = self.memory.read_register(instruction["D"]) + instruction["B"]
        self.memory.write_register(instruction["C"], self.memory.read_data(address))

    def execute_write_memory(self, instruction):
        """Записывает значение регистра в память."""
        self.memory.write_data(instruction["B"], self.memory.read_register(instruction["C"]))

    def execute_bswap(self, instruction):
        """Переставляет четыре байта и записывает результат в память."""
        value = self.memory.read_register(instruction["B"])
        if not 0 <= value <= WORD_MASK:
            raise ValueError("Значение bswap должно помещаться в 32 бита.")
        result = int.from_bytes(
            value.to_bytes(WORD_BYTES, byteorder="little"), byteorder="big"
        )
        self.memory.write_data(instruction["C"], result)

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


def parse_args():
    """Разбирает аргументы командной строки."""
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

    return parser.parse_args()


def main():
    """Запускает программу из командной строки."""
    args = parse_args()

    try:
        run_from_args(args)
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


def run_from_args(args):
    """Загружает программу, выполняет её и сохраняет дамп памяти."""
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


if __name__ == "__main__":
    main()
