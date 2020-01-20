class Test_Command:
    def __init__(self, func, cmd, *args):
        self.cmd = cmd
        self.func = func
        self.args = args

    def get_cmd_string(self):
        test = [10,21,32]
        return cmd.format(test)


class Visa_Manager:
    def __init__(self, addr):
        self.addr = addr
    #   self.rm = visa.ResourceManager('@py')
    #   self.device = self.rm.open_resource(self.addr)
    
    def query(self, cmd, *args):
        return self.device.query(cmd)

    def write(self, cmd, *args):
        return self.device.write(cmd)

    def run_test_cmd(self, test_cmd):
        pass

