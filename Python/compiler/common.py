from enum import Enum
from typing import Any


# WordType
class WordTypeEnum(Enum):
    RESERVED_WORD = 100
    OPERAND = 101
    VALUE_TYPE = 102
    COMMENT = 103
    VARIABLE_NAME = 104

    CONST = 200

    OPERATOR_ASSIGNMENT_EQUALS = 300
    OPERATOR_ARITHMETIC_ADDITION = 320
    OPERATOR_ARITHMETIC_SUBSTRACTION = 321

    IO_OUTPUT = 400
    IO_INPUT_INT = 401


class WordDetail:
    word_type: WordTypeEnum
    detail: Any | None
    word: str

    def __init__(self, word_type: WordTypeEnum, word: str, word_detail: Any | None = None) -> None:
        self.word_type = word_type
        self.detail = word_detail
        self.word = word


# WordType - Const
class ConstWordTypeDetail:
    const_name: str
    const_type: str
    is_known: bool

    def __init__(self, const_name: str, const_type: str, is_known: bool) -> None:
        self.const_name = const_name
        self.const_type = const_type
        self.is_known = is_known


class ConstWordTypeKnownTypesEnum(Enum):
    STRING = "string"
    NUM_INT = "int"
    NUM_FLOAT = "float"


# WordType - Reserved
class ReservedWordTypeDetail:
    word_in_cpp: str | None

    def __init__(self, word_in_cpp: str) -> None:
        self.word_in_cpp = word_in_cpp


# LineAction
class LineActionTypeEnum(Enum):
    SET_VARIABLE = 100
    IO_OUTPUT = 200
    IO_INPUT_INT = 201


class LineActionDetail:
    line_action_type: LineActionTypeEnum
    line_word_details: list[WordDetail]

    def __init__(self, line_action_type: LineActionTypeEnum, line_word_details: list[WordDetail]) -> None:
        self.line_action_type = line_action_type
        self.line_word_details = line_word_details


# Symbol
class SymbolTypeEnum(Enum):
    VARIABLE = 1


class SymbolVariableDetail:
    variable_value: Any | None
    variable_type: str

    def __init__(self, variable_type: str, variable_value: Any | None = None) -> None:
        self.variable_value = variable_value
        self.variable_type = variable_type


class SymbolDetail:
    symbol_name: str
    symbol_type: SymbolTypeEnum
    type_detail: SymbolVariableDetail | None

    def __init__(
        self,
        symbol_name: str,
        symbol_type: SymbolTypeEnum,
        type_detail: SymbolVariableDetail | None = None,
    ) -> None:
        self.symbol_name = symbol_name
        self.symbol_type = symbol_type
        self.type_detail = type_detail


# Defines
RESERVED_WORDS = {
    "in": WordDetail(
        word_type=WordTypeEnum.IO_INPUT_INT,
        word="in",
        word_detail=ReservedWordTypeDetail(word_in_cpp="cin >>"),
    ),
    "out": WordDetail(
        word_type=WordTypeEnum.IO_OUTPUT,
        word="out",
        word_detail=ReservedWordTypeDetail(word_in_cpp="cout <<"),
    ),
}

OPERATORS = {
    "=": WordDetail(word_type=WordTypeEnum.OPERATOR_ASSIGNMENT_EQUALS, word="="),
    "+": WordDetail(word_type=WordTypeEnum.OPERATOR_ARITHMETIC_ADDITION, word="+"),
    "-": WordDetail(word_type=WordTypeEnum.OPERATOR_ARITHMETIC_SUBSTRACTION, word="-"),
}

LINE_ACTION_STATIC_EXPRESSIONS = {
    f"{WordTypeEnum.IO_INPUT_INT.value}{WordTypeEnum.VARIABLE_NAME.value}": LineActionTypeEnum.IO_INPUT_INT,  # in a
}
LINE_ACTION_DYNAMIC_EXPRESSIONS = {
    f"{WordTypeEnum.IO_OUTPUT.value}": LineActionTypeEnum.IO_OUTPUT,  # out a+b-2...
    f"{WordTypeEnum.VARIABLE_NAME.value}{WordTypeEnum.OPERATOR_ASSIGNMENT_EQUALS.value}": LineActionTypeEnum.SET_VARIABLE,  # a = 5+9-b...
}

COMMENT_WORD = "//"

NUMERIC_TYPES = [
    type_enum.value
    for type_enum in (
        ConstWordTypeKnownTypesEnum.NUM_FLOAT,
        ConstWordTypeKnownTypesEnum.NUM_INT,
    )
]
