import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


def find_error_line(error_message: str):
    if not error_message:
        return None

    lines = error_message.splitlines()
    error_line = None

    for line in lines:
        if "line " in line:
            after_line_keyword = line.split("line ")[1]
            number_str = after_line_keyword.split(",")[0].strip()

            if number_str.isdigit():
                error_line = int(number_str)

    return error_line


def get_error_snippet(source_code: str, error_message: str):
    error_line = find_error_line(error_message)

    if error_line is None:
        return source_code

    code_lines = source_code.splitlines()
    total_lines = len(code_lines)

    start_line = error_line - 2
    if start_line < 1:
        start_line = 1

    end_line = error_line + 2
    if end_line > total_lines:
        end_line = total_lines

    snippet = ""
    for line_num in range(start_line, end_line + 1):
        line_content = code_lines[line_num - 1]

        if line_num == error_line:
            snippet += f"--> Line {line_num} (ERROR): {line_content}\n"
        else:
            snippet += f"    Line {line_num}: {line_content}\n"

    return snippet


def explain_code_error(source_code: str, error_message: str = None) -> str:
    try:
        code_snippet = get_error_snippet(source_code, error_message)

        model = genai.GenerativeModel("gemini-3.5-flash-lite")
        prompt = f"""
        Error Output:
        {error_message}

        Code to inspect:
        {code_snippet}

        Instructions:
        - Keep the answer concise.
        - Explain each line in the snippet above and show how to fix the issue.
        - Always respond in English.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
