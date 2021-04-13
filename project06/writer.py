# writer.py
# Writes to a file

class Writer:
    # Creates or overwrites (cleans) output file.
    def __init__(self, path: str) -> None:
        self.path = path
        self.file = open(self.path, "w")
        print("Opened file:", self.path)

    # Writes string to file and moves to next line.
    def write_line(self, line: str):
        self.file.write(line + "\n")

    # Required deconstructor to close file stream.
    def __del__(self):
        self.file.close()
        print("Closed file:", self.path)
