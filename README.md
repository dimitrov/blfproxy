# BLFProxy

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

## Installation
    
#### Debian/Ubuntu:

  1. Install the dependencies:

        $ sudo apt-get install python-openssl python-twisted

  2. Run the installation script:

        $ sudo ./install.sh

#### CentOS:

  1. Install the dependencies:

        $ yum install gcc python-devel pyOpenSSL
        $ wget http://www.zope.org/Products/ZopeInterface/3.3.0/zope.interface-3.3.0.tar.gz
        $ tar -xzf zope.interface-3.3.0.tar.gz
        $ cd zope.interface-3.3.0 && python setup.py install
        $ cd .. && rm -rf zope.interface-3.3.0
        $ wget -q http://twistedmatrix.com/Releases/Twisted/11.0/Twisted-11.0.0.tar.bz2
        $ tar -jxf Twisted-11.0.0.tar.bz2
        $ cd Twisted-11.0.0 && python setup.py install
        $ cd .. && rm -rf Twisted-11.0.0

  2. Run the installation script:

        $ ./install.sh

## Configuration

    TODO

## License

    Copyright (c) 2011 Dimitar Dimitrov

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

