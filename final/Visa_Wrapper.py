import visa

class Visa_Session:
    def __init__(self, addr):
        self.addr = addr
        #self.rm = visa.ResourceManager('simulated_devices.yaml@sim')
        self.rm = visa.ResourceManager('@py')
        
    def connect(self):
        self.device = self.rm.open_resource(self.addr, write_termination='\n', read_termination='\n')

    def query(self, cmd, *args):
        response = None
        #print(repr(cmd))
        try:
            response = self.device.query(cmd)
        except:
            print("Query failure")
            pass
        return response

    def write(self, cmd, *args):
        failure = False
        try:
            self.device.write(cmd)
        except:
            failure = True
            print("Write failure")
        return failure

