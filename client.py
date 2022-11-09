
from lib.argparse import Parser
from lib.connection import Connection
from lib.constant import ACK_FLAG, FIN_FLAG, SEGMENT_SIZE, SYN_ACK_FLAG, SYN_FLAG
from lib.segment import Segment


class Client:
    def __init__(self):
        args = Parser(is_server=False)
        client_port, broadcast_port, pathfile_output = args.get_values()
        self.client_port = client_port
        self.broadcast_port = broadcast_port
        self.pathfile_output = pathfile_output
        self.conn = Connection(broadcast_port=broadcast_port, port=client_port, is_server=False)
        self.segment = Segment()
        self.seq = 0
        self.ack = 0

    def connect(self):
        self.conn.send_data(self.segment.get_bytes(), (self.conn.ip, self.broadcast_port))
  
    def three_way_handshake(self):
        end = False
        while not end:
            # SYN-ACK
            data, server_addr = None, None
            try:
                data, server_addr = self.conn.listen_single_segment()
                self.segment.set_from_bytes(data)
                print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] Recieve SYN")
            except:
                print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] [Timeout] SYN response timeout")

            if self.segment.get_flag() == SYN_FLAG:
                self.segment.set_flag(["SYN", "ACK"])
                header = self.segment.get_header()
                header['ack'] = header['seq'] + 1
                header['seq'] = self.seq
                self.conn.send_data(self.segment.get_bytes(), server_addr)
                self.seq += 1
                print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] Sending SYN-ACK")
                end = True
        # RECV ACK
        self.conn.listen_single_segment()

    def sendACK(self, server_addr, ackNumber):
        response = Segment()
        response.set_flag(["ACK"])
        header = response.get_header()
        header['seq'] = 0
        header['ack'] = ackNumber
        response.set_header(header)
        self.conn.send_data(response.get_bytes(), server_addr)

    def listen_file_transfer(self):
        raw_data = b""
        rn = 0
        while True:
            try:
                data, server_addr = self.conn.listen_single_segment()
                if (server_addr[1] == self.broadcast_port):
                    self.segment.set_from_bytes(data)
                    if self.segment.valid_checksum() and self.segment.get_header()['seq'] == rn+1:
                        payload = self.segment.get_payload()
                        raw_data += payload
                        print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] Recieve Segment {rn+1}")
                        print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] Sending ACK {rn+1}")
                        self.sendACK(server_addr, rn+1)
                        rn+=1
                        continue
                    elif self.segment.get_flag() == FIN_FLAG:
                        print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] Recieve FIN")
                        break
                    elif self.segment.get_header()['seq'] < rn+1:
                        print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] Recieve Segment {self.segment.get_header()['seq']} [Duplicate]")
                    elif self.segment.get_header()['seq'] > rn+1:
                        print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] Recieve Segment {self.segment.get_header()['seq']} [Out-Of-Order]")
                    else:
                        print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] Recieve Segment {self.segment.get_header()['seq']} [Corrupt]")
                else:
                    print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] Recieve Segment {self.segment.get_header()['seq']} [Wrong port]")
                self.sendACK(server_addr, rn)
            except:
                print(f"[!] [Server {server_addr[0]}:{server_addr[1]}] [Timeout] timeout error, resending prev seq num")
                self.sendACK(server_addr, rn)
        try:
            for i in range(len(self.pathfile_output) - 1, -1, -1):
                if(self.pathfile_output[i] == '/'):
                    self.pathfile_output = self.pathfile_output[i+1:]
                    break
            file = open(f"out/{self.pathfile_output}", "wb")
            file.write(raw_data)
            file.close()
        except:
            print(f"[!] {self.pathfile_output} doesn't exists. Exiting...")
            exit(1)

if __name__ == "__main__":
    main = Client()
    main.connect()
    main.three_way_handshake()
    main.listen_file_transfer()
