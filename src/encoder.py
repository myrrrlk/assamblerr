"""Кодирование команд учебной виртуальной машины."""

COMMAND_SIZES = {
    "load_const": 4,
    "read_memory": 4,
    "write_memory": 6,
    "bswap": 6,
}
BIT_POSITIONS = {
    "load_const": {"B": 4, "C": 21},
    "read_memory": {"B": 4, "C": 16, "D": 22},
    "write_memory": {"B": 4, "C": 36},
    "bswap": {"B": 4, "C": 10},
}


def encode_instruction(instruction):
    """Собирает поля команды и возвращает байты в порядке little-endian."""
    command_name = instruction["command"]
    machine_code = instruction["A"]
    for field, shift in BIT_POSITIONS[command_name].items():
        machine_code |= instruction[field] << shift
    return machine_code.to_bytes(COMMAND_SIZES[command_name], byteorder="little")


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
