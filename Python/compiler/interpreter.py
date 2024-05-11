from typing import Iterator
from .common import *
from .core import Core


class Interpreter(Core):

    def _handle(self, line_details: Iterator[LineActionDetail]):
        for line in self._read_lines():
            # Just for get SyntaxErrors
            pass

        if not self._is_error_thrown:
            self._open_file()
            self.__run(line_details)

        if self._is_error_thrown:
            print("[!] Code Running Failed")
        else:
            print("[.] Code Runned Successfully")

    def __run(self, line_details: Iterator[LineActionDetail]) -> str:
        for line_detail in line_details:

            if line_detail.line_action_type == LineActionTypeEnum.SET_VARIABLE:
                self.__run_set_variable(line_detail)
            elif line_detail.line_action_type == LineActionTypeEnum.IO_OUTPUT:
                self.__run_output_variable(line_detail)
            elif line_detail.line_action_type == LineActionTypeEnum.IO_INPUT_INT:
                self.__run_input_int(line_detail)

    def __run_input_int(self, line_detail: LineActionDetail) -> str:
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

        input_value = None
        input_type = None
        while True:
            try:
                input_value = input(">>> Enter a number: ")
                input_value = float(input_value)
                input_type = ConstWordTypeKnownTypesEnum.NUM_FLOAT.value

                try:
                    input_value = int(input_value)
                    input_type = ConstWordTypeKnownTypesEnum.NUM_INT.value
                except Exception:
                    pass

                break

            except Exception:
                print("[!!!] Enter a valid number.")
                continue

        if symbol_exists and symbol.type_detail.variable_type != input_type:
            self._print_error(
                "TypeError",
                f"Cannot assign '{variable_name}' as '{input_type}': is already declared as '{symbol.type_detail.variable_type}'",
            )
            return

        symbol.type_detail.variable_value = input_value
        symbol.type_detail.variable_type = input_type

        self._symbol_table[variable_name] = symbol

    def __run_output_variable(self, line_detail: LineActionDetail) -> str:
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

                variable_value += f"{word_detail.word} "

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

                variable_value = f"{word_symbol.type_detail.variable_value} "

            else:
                self._print_error("SyntaxError")
                return

            variable_type = word_variable_type
            word_must_be_operator = True

        if variable_type in NUMERIC_TYPES or len(line_detail.line_word_details) > 1:
            calculated_value = eval(variable_value)
        else:
            calculated_value = variable_value

        print(calculated_value)

    def __run_set_variable(self, line_detail: LineActionDetail) -> str:
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

                variable_value += f"{word_detail.word} "

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

                variable_value += f"{word_symbol.type_detail.variable_value} "
            else:
                self._print_error("SyntaxError")
                return

            variable_type = word_variable_type
            word_must_be_operator = True

        if variable_type in NUMERIC_TYPES:
            calculated_value = eval(variable_value)
        else:
            calculated_value = variable_value

        symbol.type_detail.variable_value = calculated_value
        symbol.type_detail.variable_type = variable_type
        self._symbol_table[variable_name] = symbol
