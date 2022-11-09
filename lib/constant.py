CRC_POLYNOM = 0x1021
CRC_INIT = 0xFFFF
SEGMENT_SIZE = 32768
PAYLOAD_SIZE = SEGMENT_SIZE - 12
TIMEOUT = 30
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_BROADCAST_PORT = 9999
SYN_FLAG = 0b000000010 # 2
ACK_FLAG = 0b000010000 # 16
SYN_ACK_FLAG = ACK_FLAG | SYN_FLAG
FIN_FLAG = 0b000000001 # 1
WINDOW_SIZE = 3