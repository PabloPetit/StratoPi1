from module import  *


class Printer( Module ):

    def __init__( self, s_log_dir_path ):
        Module.__init__()

        self.s_log_dir_path = s_log_dir_path
        self.channel_dict = {}

    def register_channel( self, chan_name ):
        pass

    def is_registered( self, chan_name ):
        pass

    def log( self, chan_name, data):
        pass