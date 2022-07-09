from generator.instruction.instruction import Instruction, MultiInstruction
from generator.config.instruction_serializer import get_instruction


class Playlist:

    def __init__(self, name: str, instruction: Instruction):
        self.name: str = name
        self.instruction: Instruction = instruction

    def run(self, sp):
        songs = []
        return self.instruction.run(songs, sp)

    @classmethod
    def from_dict(cls, data):
        instructions_raw = data['instructions']
        instructions = [get_instruction(d) for d in instructions_raw]
        name = data['name']
        return Playlist(name, MultiInstruction(instructions))

