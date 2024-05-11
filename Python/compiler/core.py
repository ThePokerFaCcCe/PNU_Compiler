from abc import ABC, abstractmethod
from io import TextIOWrapper
import re
from typing import Dict, Iterator
from .common import *

REGEX_VARIABLE_NAME = "^[a-zA-Z_][a-zA-Z0-9_]*$"
REGEX_CONST_STRING = '^".*"$'
REGEX_CONST_INTEGER = "^[-+]?[0-9]*$"
REGEX_CONST_FLOAT = "^[-+]?[0-9]*\.?[0-9]+$"


class Core(ABC):

    def __init__(self, input_file_x_path: str) -> None:
        self._is_error_thrown: bool = False
        self.__cursor_current_line_number: int = 1
        self.__cursor_current_word: str = ""

        self.__input_file: TextIOWrapper = None
        self._symbol_table: Dict[str, SymbolDetail] = {}

        self.__input_file_x_path = input_file_x_path

        self._open_file()

    def _open_file(self) -> None:
        if self.__input_file:
            self.__input_file.close()

        self.__input_file = open(self.__input_file_x_path, "r")

    def _read_lines(self) -> Iterator[str]:
        line_text = self.__input_file.readline()
        while line_text:
            if line_text.strip():
                yield line_text.strip()
            self.__cursor_current_line_number += 1
            line_text = self.__input_file.readline()

    def __split_words(self, text: str) -> Iterator[str]:
        split_pattern = " |" + "|".join([f"(\\{k})" for k in OPERATORS.keys()])
        words: list[str] = re.split(split_pattern, text)

        for word in words:
            if word and word.strip():
                self.__cursor_current_word = word
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
                word_detail=ConstWordTypeDetail(
                    const_name=ConstWordTypeKnownTypesEnum.STRING.value,
                    const_type=ConstWordTypeKnownTypesEnum.STRING.value,
                    is_known=True,
                ),
            )

        is_integer_value = re.match(REGEX_CONST_INTEGER, word)
        if is_integer_value:
            return WordDetail(
                word_type=WordTypeEnum.CONST,
                word=word,
                word_detail=ConstWordTypeDetail(
                    const_name=ConstWordTypeKnownTypesEnum.NUM_INT.value,
                    const_type=ConstWordTypeKnownTypesEnum.NUM_INT.value,
                    is_known=True,
                ),
            )

        is_float_value = re.match(REGEX_CONST_FLOAT, word)
        if is_float_value:
            return WordDetail(
                word_type=WordTypeEnum.CONST,
                word=word,
                word_detail=ConstWordTypeDetail(
                    const_name=ConstWordTypeKnownTypesEnum.NUM_FLOAT.value,
                    const_type=ConstWordTypeKnownTypesEnum.NUM_FLOAT.value,
                    is_known=True,
                ),
            )

        self._print_error("SyntaxError", f"'{word}' is not a valid word", show_word=True)

    def __lex_line(self, line: str) -> list[WordDetail]:
        words = self.__split_words(line)

        word_detail_list: list[WordDetail] = []
        for word in words:
            word_detail = self.__lex_word(word)
            if not word_detail:
                return []

            word_detail_list.append(word_detail)

        return word_detail_list

    def __parse_line(self, line: str) -> LineActionDetail:
        word_detail_list = self.__lex_line(line)
        if len(word_detail_list) == 0:
            return None

        line_expression = "".join([str(word_detail.word_type.value) for word_detail in word_detail_list])  # a = 2  -> 104300200

        line_action_type = LINE_ACTION_STATIC_EXPRESSIONS.get(line_expression)
        if not line_action_type:
            for expression, action_type in LINE_ACTION_DYNAMIC_EXPRESSIONS.items():
                if line_expression.startswith(expression):
                    line_action_type = action_type
                    break

        if line_action_type:
            return LineActionDetail(
                line_action_type=line_action_type,
                line_word_details=word_detail_list,
            )
        self._print_error("SyntaxError")

    def __parse_lines(self) -> Iterator[LineActionDetail]:
        lines = self._read_lines()
        for line in lines:
            line_detail = self.__parse_line(line)
            if line_detail == None:
                continue

            yield line_detail

    def start(self):
        try:
            line_details = self.__parse_lines()
            self._handle(line_details)
        except Exception as ex:
            print("System Error!" + str(ex))

        finally:
            self.__input_file.close()

    @abstractmethod
    def _handle(self, line_details: Iterator[LineActionDetail]):
        raise NotImplementedError("Method `handle(line_details)` isn't implemented")

    def _print_error(self, error_type: str, message_detail: str = "", show_word: bool = False):
        self._is_error_thrown = True
        error_message = f"{error_type} Error in line `{self.__cursor_current_line_number}` "
        if show_word:
            error_message += f"- word `{self.__cursor_current_word}`"

        if message_detail:
            error_message += f": {message_detail}"

        print(error_message)
