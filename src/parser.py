"""Разбор YAML-программ виртуальной машины."""


import yaml


COMMANDS = {
    "load_const": {
        "A": 3,
        "fields": {
            "constant": ("B", 17),
            "address": ("C", 6),
        },
    },
    "read_memory": {
        "A": 12,
        "fields": {
            "offset": ("B", 12),
            "destination": ("C", 6),
            "base": ("D", 6),
        },
    },
    "write_memory": {
        "A": 14,
        "fields": {
            "address": ("B", 32),
            "source": ("C", 6),
        },
    },
    "bswap": {
        "A": 6,
        "fields": {
            "source": ("B", 6),
            "destination": ("C", 32),
        },
    },
}


def validate_field(name, value, bits):
    """Проверяет, помещается ли значение в заданное число бит."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"Поле '{name}' должно содержать целое число."
        )

    if value < 0 or value >= (1 << bits):
        raise ValueError(
            f"Поле '{name}' = {value} не помещается в {bits} бит."
        )


def parse_program(file_path):
    """Читает YAML и преобразует программу в список команд."""

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ValueError(f"Ошибка YAML: {error}") from error

    if not isinstance(data, dict):
        raise ValueError("Корень YAML должен быть словарем.")

    if set(data.keys()) != {"program"}:
        raise ValueError(
            "YAML должен содержать только раздел 'program'."
        )

    program = data["program"]

    if not isinstance(program, list) or not program:
        raise ValueError("Раздел 'program' должен быть непустым списком.")

    return [parse_instruction(item, index)
            for index, item in enumerate(program, start=1)]


def get_command_name(instruction, index):
    """Проверяет тип команды и её название."""
    if not isinstance(instruction, dict):
        raise ValueError(
            f"Команда №{index} должна быть словарем."
        )

    if "command" not in instruction:
        raise ValueError(
            f"У команды №{index} отсутствует поле 'command'."
        )

    command_name = instruction["command"]

    if not isinstance(command_name, str):
        raise ValueError(
            f"Название команды №{index} должно быть строкой."
        )

    if command_name not in COMMANDS:
        raise ValueError(
            f"Неизвестная команда №{index}: {command_name}"
        )

    return command_name


def validate_fields(instruction, specification, index):
    """Проверяет наличие обязательных и отсутствие лишних полей."""
    expected_fields = set(specification["fields"].keys())
    actual_fields = set(instruction.keys()) - {"command"}

    missing = expected_fields - actual_fields
    extra = actual_fields - expected_fields

    if missing:
        raise ValueError(
            f"Команда №{index}: отсутствуют поля {sorted(missing)}."
        )

    if extra:
        raise ValueError(
            f"Команда №{index}: лишние поля {sorted(extra)}."
        )


def parse_instruction(instruction, index):
    """Преобразует одну YAML-команду во внутреннее представление."""
    command_name = get_command_name(instruction, index)
    specification = COMMANDS[command_name]
    validate_fields(instruction, specification, index)
    parsed_instruction = {
        "command": command_name,
        "A": specification["A"],
    }

    for field_name, (field_code, bits) in specification["fields"].items():
        value = instruction[field_name]

        validate_field(field_name, value, bits)

        parsed_instruction[field_code] = value

    return parsed_instruction
