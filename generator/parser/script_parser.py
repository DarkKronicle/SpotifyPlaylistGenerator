from enum import Enum

from generator import DEFAULT_VALUE
from generator.parser.instruction_holder import Instructions


class Token(Enum):

    WORD = 0
    EQUALS = 1
    SEPARATOR = 2
    INSTRUCTION_START = 3
    INSTRUCTION_END = 4
    INSTRUCTION_SEPARATOR = 5
    MODIFIER_START = 6
    MODIFIER_END = 7
    DICT_DECLARATION = 8
    DICT_ELEMENT = 9


def _other(c):
    return c == "\t" or c == "\n"


class ScriptParser:

    def __init__(self, raw: str):
        self.raw = raw.strip()
        self.tokens = []
        self.data = {}

    def _tokenize(self):
        i = 0
        in_quote = False
        while i < len(self.raw):
            c = self.raw[i]
            if in_quote:
                if c == "'":
                    in_quote = False
                    i += 1
                    continue
                if c == r'\\' and i + 1 < len(self.raw) and self.raw[i + 1] == "'":
                    self.tokens.append("'")
                    i += 2
                    continue
                if not _other(c):
                    self.tokens.append(c)
                i += 1
                continue
            if c == "'":
                in_quote = True
                i += 1
                continue
            if c == '|':
                if i + 2 < len(self.raw):
                    if self.raw[i + 1] == ',' and self.raw[i + 2] == '|':
                        self.tokens.append(Token.INSTRUCTION_SEPARATOR)
                        i += 3
                        continue
                i += 1
                self.tokens.append(Token.SEPARATOR)
                continue
            if c == '=':
                self.tokens.append(Token.EQUALS)
                i += 1
                continue
            if c == '{':
                self.tokens.append(Token.INSTRUCTION_START)
                i += 1
                continue
            if c == '}':
                self.tokens.append(Token.INSTRUCTION_END)
                i += 1
                continue
            if c == '[':
                self.tokens.append(Token.MODIFIER_START)
                i += 1
                continue
            if c == ']':
                self.tokens.append(Token.MODIFIER_END)
                i += 1
                continue
            if c == '^':
                self.tokens.append(Token.DICT_DECLARATION)
                i += 1
                continue
            if c == '*':
                self.tokens.append(Token.DICT_ELEMENT)
                i += 1
                continue
            if not _other(c):
                self.tokens.append(c)
            i += 1

    def parse(self):
        self._tokenize()
        self.data = self._inner_parse(self.tokens)
        return self.data

    def _inner_parse(self, tokens: list[Token]) -> Instructions:
        # TODO put this into functions so that it's not spaghetti
        instruction_depth = 0
        modifier_depth = 0
        inner_start = -1
        raw_mod = {}
        raw_instruction = []
        current_instruction = {}
        dict_key = ""
        current_part = []
        elements = []

        for i, t in enumerate(tokens):
            if t == Token.MODIFIER_START:
                modifier_depth += 1
                if modifier_depth == 2:
                    inner_start = i
                continue
            if t == Token.MODIFIER_END:
                modifier_depth -= 1
                continue
            if t == Token.INSTRUCTION_START:
                instruction_depth += 1
                if (instruction_depth == 2 or modifier_depth == 1) and inner_start < 0:
                    inner_start = i
                elif instruction_depth == 1:
                    if current_part:
                        elements.append(current_part)
                    current_part = []
                    if len(elements) == 0:
                        # Just started
                        continue
                    if len(elements) > 2:
                        raise SyntaxError("More than one equals!")
                    if len(raw_mod.values()) == 0:
                        if elements[0][0] == Token.DICT_DECLARATION:
                            dict_key = ''.join(elements[0][1:])
                            raw_mod[dict_key] = {}
                        else:
                            raw_mod['upload'] = ''.join(elements[0])
                    else:
                        if elements[0][0] == Token.DICT_DECLARATION:
                            dict_key = ''.join(elements[0][1:])
                            raw_mod[dict_key] = {}
                        elif elements[0][0] == Token.DICT_ELEMENT:
                            if len(elements) == 1:
                                raw_mod[dict_key][''.join(elements[0][1:])] = DEFAULT_VALUE
                            else:
                                raw_mod[dict_key][''.join(elements[0][1:])] = ''.join(elements[1]) if not isinstance(elements[1], Instructions) else elements[1]
                        else:
                            if len(elements) == 1:
                                raw_mod[''.join(elements[0])] = DEFAULT_VALUE
                            else:
                                raw_mod[''.join(elements[0])] = ''.join(elements[1])
                    elements = []
                    continue
                continue
            if t == Token.INSTRUCTION_END:
                instruction_depth -= 1
                if instruction_depth == 1 or modifier_depth == 1:
                    inner_end = i + 1
                    elements.append(self._inner_parse(self.tokens[inner_start:inner_end]))
                if instruction_depth == 0 and modifier_depth == 0:
                    elements.append(''.join(current_part))
                    if len(elements) == 1 and len(current_instruction.values()) == 0:
                        current_instruction['type'] = ''.join(elements[0])
                        elements = []
                        raw_instruction.append(current_instruction)
                        current_instruction = {}
                    else:
                        current_instruction[''.join(elements[0])] = ''.join(elements[1]) if not isinstance(elements[1], Instructions) else elements[1]
                        if t == Token.INSTRUCTION_SEPARATOR:
                            raw_instruction.append(current_instruction)
                            current_instruction = {}
                        elements = []
                    if current_instruction:
                        raw_instruction.append(current_instruction)
                continue
            if instruction_depth > 1 or (instruction_depth == 1 and modifier_depth == 1):
                continue
            if t == Token.SEPARATOR or t == Token.INSTRUCTION_SEPARATOR:
                if current_part:
                    elements.append(current_part)
                current_part = []
                if len(elements) == 0:
                    raise SyntaxError("Empty element!")
                if len(elements) > 2:
                    print(elements)
                    raise SyntaxError("More than one equals!")
                if len(elements) == 1:
                    if instruction_depth == 1:
                        if len(current_instruction.values()) == 0:
                            current_instruction['type'] = ''.join(elements[0])
                            elements = []
                            if t == Token.INSTRUCTION_SEPARATOR:
                                raw_instruction.append(current_instruction)
                                current_instruction = {}
                            continue
                        raise SyntaxError("Instruction element has to have a value!")

                    # Mod time
                    if elements[0][0] == Token.DICT_DECLARATION:
                        dict_key = ''.join(elements[0][1:])
                        raw_mod[dict_key] = {}
                    elif elements[0][0] == Token.DICT_ELEMENT:
                        raw_mod[dict_key][''.join(elements[0][1:])] = DEFAULT_VALUE
                    else:
                        if len(elements) == 1 and len(raw_mod) == 0:
                            raw_mod['upload'] = ''.join(elements[0])
                        else:
                            raw_mod[''.join(elements[0])] = DEFAULT_VALUE

                    elements = []
                    continue

                # Now we're at length = 2
                if instruction_depth == 1:
                    current_instruction[''.join(elements[0])] = ''.join(elements[1])
                    if t == Token.INSTRUCTION_SEPARATOR:
                        raw_instruction.append(current_instruction)
                        current_instruction = {}
                    elements = []
                    continue

                # Modifier time
                if elements[0][0] == Token.DICT_ELEMENT:
                    raw_mod[dict_key][''.join(elements[0][1:])] = ''.join(elements[1])
                else:
                    raw_mod[''.join(elements[0])] = ''.join(elements[1])
                elements = []

                continue
            if t == Token.EQUALS:
                elements.append(current_part)
                current_part = []
                continue
            current_part.append(t)
        if instruction_depth != 0 or modifier_depth != 0:
            raise SyntaxError("Modifiers and instructions aren't properly closed!")
        return Instructions(raw_instruction, raw_mod)
