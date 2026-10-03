import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ubuntu/SJSU_intel_sys/urc_intelsys_2024/src/keyboard_typing/install/keyboard_typing'
