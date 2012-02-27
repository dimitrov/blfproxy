BLFProxy
========

BLFProxy is a simple "proxy" which connects to two or more 
Asterisk servers using the Asterisk Manager Interface, listens 
for ExtensionStatus events and updates the device states 
between the servers using the DEVICE_STATE function.

The following diagram illustrates how it works:
 _________
|         |
|  PBX A  |
|_________|
     |
     | Event: ExtensionStatus
     | Exten: 300
     | Status: 8
     |
  BLFProxy
     |
     | Action: Setvar
     | Variable: DEVICE_STATE(Custom:rhint_300)
     | Value: RINGING
 ____|____
|         |
|  PBX B  |
|_________|