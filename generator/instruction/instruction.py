class Instruction:

    def run(self, songs, sp):
        raise NotImplementedError


class MultiInstruction(Instruction):

    def __init__(self, instructions):
        self.instructions = instructions

    def run(self, songs, sp):
        for instruction in self.instructions:
            songs = instruction.run(songs, sp)
        return songs
