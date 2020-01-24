import visa

class Test_Command:
    def __init__(self, func, cmd, *args):
        self.cmd = cmd
        self.func = func
        self.args = args

    def get_cmd_string(self):
        test = [10,21,32]
        return cmd.format(test)


class Visa_Session:
    def __init__(self, addr):
        self.addr = addr
        self.rm = visa.ResourceManager('@py')
        
    def connect(self):
        self.device = self.rm.open_resource(self.addr)

    def query(self, cmd, *args):
        response = None
        try:
            self.device.query(cmd)
        except:
            pass

        return response

    def write(self, cmd, *args):
        failure = False
        try:
            self.device.write(cmd)
        except:
            failure = True
        
        return failure

    def run_test_cmd(self, test_cmd):
        pass

