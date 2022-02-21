import os
import re
from schablonesk.tokens import Token
from schablonesk.token_category import *
from schablonesk.config import Config


class Scanner:

    def __init__(self):
        pattern = Config.get().get_cmd_line_begin()
        self.cmd_line_begin = re.compile("^\\s*" + pattern + "(.+)")

    def scan(self, code):
        ret = []
        for block in self._scan_lines(code.split("\n")):
            ret += block.tokenize()
        return ret

    def _scan_lines(self, lines):
        blocks = []
        command_block = None
        text_block = None

        for line_num, line in enumerate(lines):
            line_num += 1  # start line counting from 1
            match = self.cmd_line_begin.match(line)
            if match:
                if text_block is not None:
                    blocks.append(text_block)
                    text_block = None
                if command_block is None:
                    command_block = _CommandBlock()
                command_block.add(line_num, match.group(1))
            else:
                if command_block is not None:
                    blocks.append(command_block)
                    command_block = None
                if text_block is None:
                    text_block = _TextBlock(line_num)
                text_block.add_text_line(line)

        if command_block is not None:
            blocks.append(command_block)
        if text_block is not None:
            blocks.append(text_block)

        return blocks


class _CommandBlock:

    def __init__(self):
        self.lines = []
        self.patterns = [
            (re.compile("\\."), DOT),
            (re.compile("=="), EQ),
            (re.compile("<>"), NE),
            (re.compile(">"), GT),
            (re.compile(">="), GE),
            (re.compile("<"), LT),
            (re.compile("<="), LE),
            (re.compile("="), ASSIGN),
            (re.compile("\\("), LPAR),
            (re.compile("\\)"), RPAR),
            (re.compile("^[a-z_][a-z0-9_]*"), IDENTIFIER),
            (re.compile(r"'(\\'|[^'])*'"), STRING),
            (re.compile("\\d+"), INT),
            (re.compile("\\d+\\.\\d*"), REAL)
        ]
        self.whitespace = re.compile("^\\s+")
        self.keywords = {
            "cond": COND,
            "else": ELSE,
            "endcond": ENDCOND,
            "for": FOR,
            "in": IN,
            "where": WHERE,
            "endfor": ENDFOR,
            "and": AND,
            "or": OR,
            "not": NOT,
            "true": TRUE,
            "false": FALSE
        }

    def add(self, line_num, commands):
        self.lines.append((line_num, commands))

    def tokenize(self):
        all_tokens = []
        for line_num, commands in self.lines:
            all_tokens += self._tokenize_commands(line_num, commands)
        return all_tokens

    def _tokenize_commands(self, line_num, commands):
        tokens = []
        remaining = commands
        while remaining:
            token, remaining = self.match_next(remaining, line_num)
            if token is not None:
                tokens.append(token)
        return tokens

    def match_next(self, s, line_num):
        remaining = s

        # Skip whitespace
        match_res = self.whitespace.match(remaining)

        if match_res:
            remaining = remaining[match_res.end():]
        if not remaining:
            return None, remaining

        # Find maximal munch:
        max_token_catg = None
        max_size = 0
        for regex, token_catg in self.patterns:
            match_res = regex.match(remaining)
            if match_res:
                size = match_res.end()
                if max_token_catg is None or size > max_size:
                    max_token_catg = token_catg
                    max_size = size
        if max_token_catg:
            lexeme = remaining[:max_size]
            # Check for keywords:
            max_token_catg = self.adapt_token_catg(max_token_catg, lexeme)
            return Token(max_token_catg,
                         lexeme,
                         line_num), remaining[max_size:]
        else:
            return Token(UNKNOWN, remaining, line_num), ""

    def adapt_token_catg(self, token_catg, lexeme):
        if token_catg != IDENTIFIER or lexeme not in self.keywords:
            return token_catg
        else:
            return self.keywords[lexeme]


class _TextBlock:

    def __init__(self, start_line_num):
        self.text = ""
        self.start_line_num = start_line_num

    def add_text_line(self, line):
        if self.text:
            self.text += os.linesep + line
        else:
            self.text = line

    def tokenize(self):
        return [Token(TEXT, self.text, self.start_line_num)]
