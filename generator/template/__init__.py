def set_variables(data: dict, variables: dict):
    pass


class Template:

    def __init__(self, raw_data: dict, name):
        self.raw_data = raw_data
        self.name = name

    async def get_songs(self, variables):
        playlist = self.raw_data['template']

