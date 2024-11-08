import pandas as pd
import argparse
import sys
from pathlib import Path

def excel_to_markdown(input_file, output_file=None, sheet_name=0):
    """
    Convert Excel file to Markdown format

    Args:
        input_file (str): Path to input Excel file
        output_file (str, optional): Path to output Markdown file. If None, prints to stdout
        sheet_name (str/int, optional): Sheet name or index to convert. Defaults to 0 (first sheet)
    """
    try:
        # Read Excel file
        df = pd.read_excel(input_file, sheet_name=sheet_name)

        # Convert DataFrame to Markdown
        # Get the filename without extension
        filename = Path(input_file).stem
        markdown = f"# {filename}\n\n"

        # Add table headers
        headers = "|" + "|".join(str(col) for col in df.columns) + "|"
        separator = "|" + "|".join("---" for _ in df.columns) + "|"

        markdown += headers + "\n"
        markdown += separator + "\n"

        # Add table rows
        for _, row in df.iterrows():
            markdown += "|" + "|".join(str(cell) for cell in row) + "|\n"

        # Output handling
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"Conversion complete. Output saved to: {output_file}")
        else:
            print(markdown)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert Excel file to Markdown format')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('-o', '--output', help='Path to output Markdown file (optional)')
    parser.add_argument('-s', '--sheet', help='Sheet name or index (default: 0)', default=0)

    # Parse arguments
    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Validate file extension
    if input_path.suffix.lower() not in ['.xlsx', '.xls', '.xlsm']:
        print("Error: Input file must be an Excel file (.xlsx, .xls, or .xlsm)", file=sys.stderr)
        sys.exit(1)

    # Convert sheet name to int if it's a number
    try:
        sheet = int(args.sheet)
    except ValueError:
        sheet = args.sheet

    # Perform conversion
    excel_to_markdown(args.input_file, args.output, sheet)

if __name__ == "__main__":
    main()
