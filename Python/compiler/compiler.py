from typing import Iterator
from .common import *
from .core import Core


BASE_CPP_CODE = """
#include <iostream>
using namespace std;

int main()
{{
{0}
    
    return 0;
}}
"""


class Compiler(Core):

    def __init__(self, input_file_x_path: str, output_file_cpp_path: str) -> None:
        super().__init__(input_file_x_path)
        self.__output_file_cpp_path: str = output_file_cpp_path

    def _handle(self, line_details: Iterator[LineActionDetail]):
        compiled_text = self.__compile(line_details)

        if not self._is_error_thrown:
            self.__save_compiled_file(compiled_text, self.__output_file_cpp_path)

    def __compile(self, line_details: Iterator[LineActionDetail]) -> str:
        compiled_text = ""
        for line_detail in line_details:
            compiled_text += "\t"

            if line_detail.line_action_type == LineActionTypeEnum.SET_VARIABLE:
                compile_line_result = self.__compile_set_variable(line_detail)
            elif line_detail.line_action_type == LineActionTypeEnum.IO_OUTPUT:
                compile_line_result = self.__compile_output_variable(line_detail)
            elif line_detail.line_action_type == LineActionTypeEnum.IO_INPUT_INT:
                compile_line_result = self.__compile_input_int(line_detail)

            if compile_line_result:
                compiled_text += compile_line_result
            compiled_text += "\n"

        return BASE_CPP_CODE.format(compiled_text)

    def __compile_input_int(self, line_detail: LineActionDetail) -> str:
        input_command_detail: ReservedWordTypeDetail = line_detail.line_word_details[0].detail
        input_command = input_command_detail.word_in_cpp

        variable_name = line_detail.line_word_details[1].word

        symbol = self._symbol_table.get(variable_name)
        symbol_exists = False
        if symbol:
            if symbol.symbol_type != SymbolTypeEnum.VARIABLE:
                self._print_error("TypeError", f"Cannot use '{variable_name}': is not variable")
                return

            symbol_exists = True

        else:
            symbol = SymbolDetail(
                symbol_type=SymbolTypeEnum.VARIABLE,
                symbol_name=variable_name,
                type_detail=SymbolVariableDetail(
                    variable_type=ConstWordTypeKnownTypesEnum.NUM_INT.value,
                    variable_value=None,
                ),
            )

        if symbol_exists and symbol.type_detail.variable_type not in NUMERIC_TYPES:
            self._print_error("TypeError", f"Cannot use '{variable_name}': is not numeric type")
            return

        if symbol_exists:
            return f"{input_command} {variable_name};"
        else:
            self._symbol_table[variable_name] = symbol
            return f"{symbol.type_detail.variable_type} {variable_name};\n" + f"\t{input_command} {variable_name};"

    def __compile_output_variable(self, line_detail: LineActionDetail) -> str:
        output_command_detail: ReservedWordTypeDetail = line_detail.line_word_details[0].detail
        output_command = output_command_detail.word_in_cpp

        variable_value = ""
        variable_type = None
        word_must_be_operator = False
        for word_detail in line_detail.line_word_details[1:]:
            word_variable_type = None
            if word_must_be_operator and word_detail.word_type.name.startswith("OPERATOR_ARITHMETIC"):
                word_must_be_operator = False
                variable_value += f"{word_detail.word} "
                continue

            elif word_detail.word_type == WordTypeEnum.CONST:
                variable_type_detail: ConstWordTypeDetail = word_detail.detail
                word_variable_type = variable_type_detail.const_type
                if variable_type and word_variable_type != variable_type:
                    self._print_error(
                        "TypeError",
                        f"Cannot use operators between '{word_variable_type}' and '{variable_type}': is not supported",
                    )
                    return

            elif word_detail.word_type == WordTypeEnum.VARIABLE_NAME:
                word_symbol = self._symbol_table.get(word_detail.word)
                if not word_symbol:
                    self._print_error("ValueError", f"variable '{word_detail.word}' is not defined")
                    return

                if word_symbol.symbol_type != SymbolTypeEnum.VARIABLE:
                    raise ValueError(f"'{word_detail.word}' is not a variable")

                word_variable_type = word_symbol.type_detail.variable_type
                if variable_type and word_variable_type != variable_type:
                    self._print_error(
                        "ValueError",
                        f"Cannot use operators between '{word_variable_type}' and '{variable_type}': is not supported",
                    )
                    return

            else:
                self._print_error("SyntaxError")
                return

            variable_value += f"{word_detail.word} "
            variable_type = word_variable_type
            word_must_be_operator = True

        variable_value = variable_value.strip()
        return f"{output_command} {variable_value};"

    def __compile_set_variable(self, line_detail: LineActionDetail) -> str:
        variable_name = line_detail.line_word_details[0].word

        variable_value = ""
        variable_type = None

        symbol = self._symbol_table.get(variable_name)
        symbol_exists = False
        if symbol:
            if symbol.symbol_type != SymbolTypeEnum.VARIABLE:
                self._print_error("TypeError", f"Cannot use '{variable_name}': is not variable")
                return

            variable_type = symbol.type_detail.variable_type
            symbol_exists = True

        else:
            symbol = SymbolDetail(
                symbol_type=SymbolTypeEnum.VARIABLE,
                symbol_name=variable_name,
                type_detail=SymbolVariableDetail(variable_type=variable_type, variable_value=variable_value),
            )

        word_must_be_operator = False
        for word_detail in line_detail.line_word_details[2:]:
            word_variable_type = None
            if word_must_be_operator and word_detail.word_type.name.startswith("OPERATOR_ARITHMETIC"):
                word_must_be_operator = False
                variable_value += f"{word_detail.word} "
                continue

            elif word_detail.word_type == WordTypeEnum.CONST:
                variable_type_detail: ConstWordTypeDetail = word_detail.detail
                word_variable_type = variable_type_detail.const_type
                if variable_type and word_variable_type != variable_type:
                    self._print_error(
                        "TypeError",
                        f"Cannot assign '{variable_name}' as '{word_variable_type}': is already declared as '{variable_type}'",
                    )
                    return

            elif word_detail.word_type == WordTypeEnum.VARIABLE_NAME:
                word_symbol = self._symbol_table.get(word_detail.word)
                if not word_symbol:
                    raise ValueError(f"variable '{word_detail.word}' is not defined")

                if word_symbol.symbol_type != SymbolTypeEnum.VARIABLE:
                    raise ValueError(f"'{word_detail.word}' is not a variable")

                word_variable_type = word_symbol.type_detail.variable_type
                if variable_type and word_variable_type != variable_type:
                    self._print_error(
                        "TypeError",
                        f"Cannot assign '{variable_name}' as '{word_variable_type}': is already declared as '{variable_type}'",
                    )
                    return
            else:
                self._print_error("SyntaxError")
                return

            variable_value += f"{word_detail.word} "
            variable_type = word_variable_type
            word_must_be_operator = True

        variable_value = variable_value.strip()
        symbol.type_detail.variable_value = variable_value
        symbol.type_detail.variable_type = variable_type
        self._symbol_table[variable_name] = symbol

        if symbol_exists:
            return f"{variable_name} = {variable_value};"
        else:
            return f"{variable_type} {variable_name} = {variable_value};"

    def __save_compiled_file(self, compiled_text: str, output_cpp_path: str):
        try:
            with open(output_cpp_path, "w", encoding="utf-8") as output_file:
                output_file.write(compiled_text)
        except Exception as ex:
            self.__input_file.close()
            print(f"Error save file to '{output_cpp_path}' : {ex}")
