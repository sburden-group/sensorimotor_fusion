import serial
import serial.tools.list_ports

print([(p.device,p.description) for p in serial.tools.list_ports.comports()])
