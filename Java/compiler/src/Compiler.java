import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

/**
 * کلاس Compiler برای تبدیل کد زبان X به کد C++ استفاده می‌شود.
 */
public class Compiler {

    // تعریف ثابت‌های نشانگر نوع توکن‌ها
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

    /**
     * متدی برای خواندن محتوای یک فایل به صورت خط به خط
     * 
     * @param path مسیر فایل
     * @return لیستی از خطوط فایل
     */
    public static List<String> readFile(String path) {
        List<String> fileLines = new ArrayList<String>();

        try {
            fileLines = Files.readAllLines(Paths.get(path), StandardCharsets.UTF_8);
        } catch (Exception e) {
            System.out.println("Error reading file");
        }

        return fileLines;
    }

    /**
     * متدی برای نوشتن محتوای رشته به یک فایل
     * 
     * @param path    مسیر فایل
     * @param content محتوای قابل نوشتن
     */
    public static void writeFile(String path, String content) {
        try {
            List<String> lines = Arrays.asList(content.split("\n"));
            Files.write(Paths.get(path), lines, StandardCharsets.UTF_8);
        } catch (Exception e) {
            System.out.println("Error writing file");
        }
    }

    /**
     * یک متد برای بررسی اینکه آیا یک رشته می‌تواند به صورت عدد صحیح تبدیل شود یا
     * خیر
     * 
     * @param value رشته مورد بررسی
     * @return true اگر رشته به عدد صحیح تبدیل شود، در غیر این صورت false
     */
    public static boolean isStringInteger(String value) {
        try {
            Integer.parseInt(value);
        } catch (Exception e) {
            return false;
        }
        return true;
    }

    /**
     * یک متد برای بررسی اینکه آیا یک رشته نشانگر یک اپرند (عملگر) است یا خیر
     * 
     * @param value رشته مورد بررسی
     * @return true اگر رشته یک اپرند باشد، در غیر این صورت false
     */
    public static boolean isStringOperand(String value) {
        if (value.length() < 1)
            return false;

        char firstChar = value.charAt(0);
        if (isStringInteger(String.valueOf(firstChar)))
            return false;

        return true;
    }

    /**
     * متدی برای تجزیه خط متنی به توکن‌ها
     * 
     * @param words لیستی از کلمات موجود در خط
     * @return لیستی از توکن‌های تجزیه شده
     */
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

    /**
     * متدی برای تجزیه و تحلیل کد و تبدیل آن به کد C++
     * 
     * @param lines لیستی از خطوط کد زبان X
     * @return کد C++ تولید شده
     */
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

    /**
     * متدی برای تبدیل یک فایل زبان X به کد C++
     * 
     * @param input  مسیر فایل ورودی زبان X
     * @param output مسیر فایل خروجی کد C++
     */
    public static void compileFile(String input, String output) {
        try {
            List<String> inputFileContent = readFile(input);
            String compiledString = parse(inputFileContent);
            writeFile(output, compiledString);
        } catch (Exception e) {
            System.out.println("Something bad happened during compiling");
        }
    }

    /**
     * متد main برای اجرای برنامه
     * 
     * @param args آرگومان‌های خط فرمان
     */
    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.out.println("Bad arguments given! example: java Compiler.java path/to/input path/to/output");
        }
        String inputFilePath = args[0];
        String outputFilePath = args[1];
        compileFile(inputFilePath, outputFilePath);
    }
}
