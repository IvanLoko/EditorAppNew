class NonePointError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'NonePointsError, {self.message}. There is no points in area'
        else:
            return 'There is no poin in area'