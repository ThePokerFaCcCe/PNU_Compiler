import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

public class Compiler {

    public static int IN = 1;
    public static int OUT = 2;
    public static int EQUALS = 3;
    public static int MULTIPLY = 4;
    public static int PLUS = 5;
    public static int MINUS = 6;
    public static int DIVIDE = 7;
    public static int OPERAND = 100;
    public static int INTEGER = 101;

    public static Scanner console = new Scanner(System.in);

    public static List<String> readFile(String path) {
        List<String> fileLines = new ArrayList<String>();

        try {
            fileLines = Files.readAllLines(Paths.get(path), StandardCharsets.UTF_8);
        } catch (Exception e) {
            System.out.println("Error reading file");
        }

        return fileLines;
    }

    public static void writeFile(String path, String content) {
        try {
            List<String> lines = Arrays.asList(content.split("\n"));
            Files.write(Paths.get(path), lines, StandardCharsets.UTF_8);
        } catch (Exception e) {
            System.out.println("Error writing file");
        }
    }

    public static boolean isStringInteger(String value) {
        try {
            Integer.parseInt(value);
        } catch (Exception e) {
            return false;
        }
        return true;
    }

    public static boolean isStringOperand(String value) {
        if (value.length() < 1)
            return false;

        char firstChar = value.charAt(0);
        if (isStringInteger(String.valueOf(firstChar)))
            return false;

        return true;
    }

    public static List<Integer> lexLine(String[] words) {
        List<Integer> tokens = new ArrayList<Integer>();

        for (String word : words) {
            if (word.length() == 0)
                continue;
            else if (word.equals("in"))
                tokens.add(IN);
            else if (word.equals("out"))
                tokens.add(OUT);
            else if (word.equals("="))
                tokens.add(EQUALS);
            else if (word.equals("*"))
                tokens.add(MULTIPLY);
            else if (word.equals("+"))
                tokens.add(PLUS);
            else if (word.equals("-"))
                tokens.add(MINUS);
            else if (word.equals("/"))
                tokens.add(DIVIDE);
            else if (isStringInteger(word))
                tokens.add(INTEGER);
            else if (isStringOperand(word))
                tokens.add(OPERAND);
            else {
                return null;
            }
        }

        return tokens;
    }

    public static String parse(List<String> lines) {
        String compiledCode = "";

        List<String> symbols = new ArrayList<String>();

        int lineCounter = 1;
        for (String lineText : lines) {
            String[] splittedText = lineText.trim().split(" ");
            List<Integer> lexResult = lexLine(splittedText);
            if (lexResult == null) {
                System.out.printf("Invalid Syntax: Line %s\n", lineCounter);
                lineCounter++;
                continue;
            }
            if (lexResult.size() == 0) {
                lineCounter++;
                continue;
            } else if (lexResult.size() == 2) {
                if (lexResult.get(0) == IN && lexResult.get(1) == OPERAND) {
                    String symbol = splittedText[1];
                    if (symbols.indexOf(symbol) == -1) {
                        symbols.add(symbol);
                    }
                    compiledCode += "cin >> " + symbol + ";\n";
                    lineCounter++;
                    continue;
                }
            } else if (lexResult.size() > 2) {
                boolean isVariableDeclaring = false;
                if (lexResult.get(0) == OPERAND) {
                    String symbol = splittedText[0];
                    if (symbols.indexOf(symbol) == -1) {
                        symbols.add(symbol);
                    }
                    isVariableDeclaring = true;
                    compiledCode += symbol + " = ";
                } else if (lexResult.get(0) == OUT) {
                    compiledCode += "cout << ";
                } else {
                    System.out.printf("Invalid Syntax: Line %s\n", lineCounter);
                    lineCounter++;
                    continue;
                }

                boolean isFirstItem = true;
                boolean skipFirstEqualSign = isVariableDeclaring;
                boolean mustBeOperator = false;
                int textIndex = 0;
                for (int token : lexResult) {
                    if (isFirstItem) {
                        isFirstItem = false;
                        textIndex++;
                        continue;
                    }
                    if (token == EQUALS && skipFirstEqualSign) {
                        skipFirstEqualSign = false;
                        textIndex++;
                        continue;
                    }
                    if (mustBeOperator) {
                        if (token != PLUS && token != MINUS && token != DIVIDE && token != MULTIPLY) {
                            System.out.printf("Invalid Syntax: Line %s\n", lineCounter);
                            textIndex++;
                            continue;
                        }
                        mustBeOperator = false;
                    } else {
                        if (token != OPERAND && token != INTEGER) {
                            System.out.printf("Invalid Syntax: Line %s\n", lineCounter);
                            textIndex++;
                            continue;
                        } else if (token == OPERAND) {
                            String symbol = splittedText[textIndex];
                            if (symbols.indexOf(symbol) == -1) {
                                System.out.printf("Variable %s not found: Line %s\n", symbol, lineCounter);
                                textIndex++;
                                continue;
                            }
                        }
                        mustBeOperator = true;
                    }

                    compiledCode += splittedText[textIndex];
                    textIndex++;
                }

                compiledCode += ";\n";
                lineCounter++;
            }

        }

        String compiledSymbols = "";
        for (String symbol : symbols) {
            compiledSymbols += "int " + symbol + ";\n";
        }

        String compiledResult = "#include <iostream>\n" + //
                "using namespace std;\n" + //
                "int main()\n" + //
                "{\n" +
                compiledSymbols + compiledCode + //
                "return 0;\n" + //
                "}";
        return compiledResult;
    }

    public static void compileFile(String input, String output) {
        try {
            List<String> inputFileContent = readFile(input);
            String compiledString = parse(inputFileContent);
            writeFile(output, compiledString);
        } catch (Exception e) {
            System.out.println("Something bad happened during compiling");
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.out.println("Bad arguments given! example: java Compiler.java path/to/input path/to/output");
        }
        String inputFilePath = args[0];
        String outputFilePath = args[1];
        compileFile(inputFilePath, outputFilePath);
    }
}
