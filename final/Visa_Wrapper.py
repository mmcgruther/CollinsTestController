import visa

class Visa_Session:
    def __init__(self, addr, backend):
        self.addr = addr
        self.rm = visa.ResourceManager(backend)
        
    def connect(self, w_term, r_term):
        failure = False
        try:
            self.device = self.rm.open_resource(self.addr, write_termination=w_term, read_termination=r_term)
        except:
            failure = True
        return failure

    def query(self, cmd, *args):
        response = None
        try:
            response = self.device.query(cmd)
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

