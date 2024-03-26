from enum import Enum
from io import TextIOWrapper
import os
import re
from typing import Any, Dict, Iterator

REGEX_VARIABLE_NAME = "^[a-zA-Z_][a-zA-Z0-9_]*$"
REGEX_CONST_STRING = '^".*"$'
REGEX_CONST_INTEGER = "^[-+]?[0-9]*$"
REGEX_CONST_FLOAT = "^[-+]?[0-9]*\.?[0-9]+$"


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


class ConstTypeDetail:
    const_name: str
    const_type: str
    is_known: bool

    def __init__(self, const_name: str, const_type: str, is_known: bool) -> None:
        self.const_name = const_name
        self.const_type = const_type
        self.is_known = is_known


class WordDetail:
    word_type: WordTypeEnum
    detail: Any | None
    word: str

    def __init__(
        self, word_type: WordTypeEnum, word: str, word_detail: Any | None = None
    ) -> None:
        self.word_type = word_type
        self.detail = word_detail
        self.word = word


class ReservedWordTypeEnum(Enum):
    VALUE_TYPE = WordTypeEnum.VALUE_TYPE


class ReservedWordDetail:
    reserved_type: ReservedWordTypeEnum
    word_in_cpp: str | None

    def __init__(self, reserved_type: ReservedWordTypeEnum, word_in_cpp: str) -> None:
        self.reserved_type = reserved_type
        self.word_in_cpp = word_in_cpp


RESERVED_WORDS = {
    "int": WordDetail(
        word_type=WordTypeEnum.RESERVED_WORD,
        word="int",
        word_detail=ReservedWordDetail(
            reserved_type=ReservedWordTypeEnum.VALUE_TYPE, word_in_cpp="int"
        ),
    ),
}

OPERATORS = {
    "=": WordDetail(word_type=WordTypeEnum.OPERATOR_ASSIGNMENT_EQUALS, word="="),
    "+": WordDetail(word_type=WordTypeEnum.OPERATOR_ARITHMETIC_ADDITION, word="+"),
    "-": WordDetail(word_type=WordTypeEnum.OPERATOR_ARITHMETIC_SUBSTRACTION, word="-"),
}

COMMENT_WORD = "//"


class LineActionTypeEnum(Enum):
    DECLARE_VARIABLE = 1
    SET_VARIABLE = 2
    DECLARE_AND_SET_VARIABLE = 3


class LineActionDetail:
    line_action_type: LineActionTypeEnum
    line_word_details: list[WordDetail]

    def __init__(
        self, line_action_type: LineActionTypeEnum, line_word_details: list[WordDetail]
    ) -> None:
        self.line_action_type = line_action_type
        self.line_word_details = line_word_details


LINE_ACTION_EXPRESSIONS = {
    f"{WordTypeEnum.VARIABLE_NAME.value}{WordTypeEnum.OPERATOR_ASSIGNMENT_EQUALS.value}": LineActionTypeEnum.SET_VARIABLE
}


BASE_CPP_CODE = """
#include <iostream>
using namespace std;

int main()
{{
{0}
    
    return 0;
}}
"""


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


class Compiler:
    def __init__(self) -> None:
        self.__input_file: TextIOWrapper = None
        self.__symbol_table: Dict[str, SymbolDetail] = {}

    def __read_lines(self) -> Iterator[str]:
        line_text = self.__input_file.readline()
        while len(line_text) > 0:
            yield line_text
            line_text = self.__input_file.readline()

    def __split_words(self, text: str) -> Iterator[str]:
        split_pattern = " |" + "|".join([f"(\\{k})" for k in OPERATORS.keys()])
        words: list[str] = re.split(split_pattern, text)

        # words: list[str] = text.split(" ")
        for word in words:
            if word and word.strip():
                yield word.strip()

    def __lex_word(self, word: str) -> WordDetail:
        if word == COMMENT_WORD:
            return WordDetail(word_type=WordTypeEnum.COMMENT, word=COMMENT_WORD)

        reserved_word_detail = RESERVED_WORDS.get(word)
        if reserved_word_detail != None:
            return reserved_word_detail

        operator_word_detail = OPERATORS.get(word)
        if operator_word_detail != None:
            return operator_word_detail

        is_variable_name = re.match(REGEX_VARIABLE_NAME, word)
        if is_variable_name:
            return WordDetail(word_type=WordTypeEnum.VARIABLE_NAME, word=word)

        is_string_value = re.match(REGEX_CONST_STRING, word)
        if is_string_value:
            return WordDetail(
                word_type=WordTypeEnum.CONST,
                word=word,
                word_detail=ConstTypeDetail(
                    const_name="string", const_type="string", is_known=True
                ),
            )

        is_integer_value = re.match(REGEX_CONST_INTEGER, word)
        if is_integer_value:
            return WordDetail(
                word_type=WordTypeEnum.CONST,
                word=word,
                word_detail=ConstTypeDetail(
                    const_name="integer", const_type="int", is_known=True
                ),
            )

        is_float_value = re.match(REGEX_CONST_FLOAT, word)
        if is_float_value:
            return WordDetail(
                word_type=WordTypeEnum.CONST,
                word=word,
                word_detail=ConstTypeDetail(
                    const_name="float", const_type="float", is_known=True
                ),
            )

        raise SyntaxError(f"'{word}' is not a valid word")

    def __lex_line(self, line: str) -> list[WordDetail]:
        words = self.__split_words(line)

        word_detail_list: list[WordDetail] = []
        for word in words:
            word_detail = self.__lex_word(word)
            word_detail_list.append(word_detail)

        return word_detail_list

    def __parse_line(self, line: str) -> LineActionDetail:
        word_detail_list = self.__lex_line(line)
        if len(word_detail_list) == 0:
            return None

        line_expression = "".join(
            [str(word_detail.word_type.value) for word_detail in word_detail_list]
        )

        for expression, action_type in LINE_ACTION_EXPRESSIONS.items():
            if line_expression.startswith(expression):
                return LineActionDetail(
                    line_action_type=action_type,
                    line_word_details=word_detail_list,
                )

        raise SyntaxError(f"Syntax Error Near {line}")

    def __parse(self):
        lines = self.__read_lines()
        compiled_text = ""
        for line in lines:
            line_detail = self.__parse_line(line)
            if line_detail == None:
                continue

            compiled_text += "\t"

            if line_detail.line_action_type == LineActionTypeEnum.SET_VARIABLE:
                compiled_text += self.__compile_set_variable(line_detail)

            compiled_text += "\n"

        return compiled_text

    def __compile_set_variable(self, line_detail: LineActionDetail) -> str:
        variable_name = line_detail.line_word_details[0]
        variable_value = line_detail.line_word_details[2]

        variable_type_detail: ConstTypeDetail = variable_value.detail
        variable_type = variable_type_detail.const_type

        is_symbol_created = self.__create_or_update_symbol_variable(
            variable_name.word, variable_value.word, variable_type
        )
        if is_symbol_created:
            return f"{variable_type} {variable_name.word} = {variable_value.word};"
        else:
            return f"{variable_name.word} = {variable_value.word};"

    def __create_or_update_symbol_variable(
        self, variable_name: str, variable_value: str, variable_type: str
    ) -> bool:
        exists_symbol = self.__symbol_table.get(variable_name)

        if exists_symbol:
            if exists_symbol.symbol_type != SymbolTypeEnum.VARIABLE:
                raise TypeError(f"Cannot use '{variable_name}': is not variable")

            exists_variable_type = exists_symbol.type_detail.variable_type
            if exists_variable_type != variable_type:
                raise TypeError(
                    f"Cannot declare '{variable_name}' as '{variable_type}': is already declared as '{exists_variable_type}'"
                )

            exists_symbol.type_detail.variable_value = variable_value
            return False

        else:
            self.__symbol_table[variable_name] = SymbolDetail(
                symbol_type=SymbolTypeEnum.VARIABLE,
                symbol_name=variable_name,
                type_detail=SymbolVariableDetail(
                    variable_type=variable_type, variable_value=variable_value
                ),
            )
            return True

    def compile_file(self, input_x_path: str, output_cpp_path: str):
        # TODO - check file types & exists
        self.__input_file = open(input_x_path, "r", encoding="utf-8")

        try:
            compiled_code = self.__parse()
            cpp_code = BASE_CPP_CODE.format(compiled_code)

            with open(output_cpp_path, "w", encoding="utf-8") as output_file:
                output_file.write(cpp_code)

        except Exception as ex:
            self.__input_file.close()
            raise ex
