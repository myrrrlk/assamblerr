
try:
    from .parser import COMMANDS
except ImportError:
    from parser import COMMANDS

def encode_instruction(instruction):
    """
    Преобразует одну команду из промежуточного
    представления в машинный код.
    """

    command_name = instruction["command"]
    specification = COMMANDS[command_name]

    # Размер команды в байтах.
    sizes = {
        "load_const": 4,
        "read_memory": 4,
        "write_memory": 6,
        "bswap": 6,
    }

    size = sizes[command_name]

    # Собираем все поля команды в одно целое число.
    machine_code = 0

    # Поле A всегда начинается с нулевого бита.
    machine_code |= instruction["A"]

    # Получаем расположение остальных полей.
    bit_positions = {
        "load_const": {
            "B": 4,
            "C": 21,
        },
        "read_memory": {
            "B": 4,
            "C": 16,
            "D": 22,
        },
        "write_memory": {
            "B": 4,
            "C": 36,
        },
        "bswap": {
            "B": 4,
            "C": 10,
        },
    }

    positions = bit_positions[command_name]

    for field, shift in positions.items():
        machine_code |= instruction[field] << shift

    # Переводим число в последовательность байтов.
    # Порядок байтов — little-endian.
    return machine_code.to_bytes(size, byteorder="little")


def encode_program(program):
    """
    Преобразует всю программу в машинное представление.
    """

    result = bytearray()

    for instruction in program:
        result.extend(encode_instruction(instruction))

    return bytes(result)


def save_binary(program, output_path):
    """
    Записывает машинный код в двоичный файл.
    """

    machine_code = encode_program(program)

    with open(output_path, "wb") as file:
        file.write(machine_code)

    return len(machine_code)
