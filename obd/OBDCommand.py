
########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2009 Peter J. Creath                                       #
# Copyright 2016 Brendan Whitfield (brendan-w.com)                     #
#                                                                      #
########################################################################
#                                                                      #
# OBDCommand.py                                                        #
#                                                                      #
# This file is part of python-OBD (a derivative of pyOBD)              #
#                                                                      #
# python-OBD is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 2 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# python-OBD is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with python-OBD.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                      #
########################################################################

from .utils import *
from .debug import debug
from .protocols import ECU
from .OBDResponse import OBDResponse


class OBDCommand():
    def __init__(self,
                 name,
                 desc,
                 command,
                 _bytes,
                 decoder,
                 ecu=ECU.ALL,
                 fast=False):
        self.name      = name        # human readable name (also used as key in commands dict)
        self.desc      = desc        # human readable description
        self.command   = command     # command string
        self.bytes     = _bytes      # number of bytes expected in return
        self.decode    = decoder     # decoding function
        self.ecu       = ecu         # ECU ID from which this command expects messages from
        self.fast      = fast        # can an extra digit be added to the end of the command? (to make the ELM return early)

    def clone(self):
        return OBDCommand(self.name,
                          self.desc,
                          self.command,
                          self.bytes,
                          self.decode,
                          self.ecu,
                          self.fast)

    @property
    def mode_int(self):
        if len(self.command) >= 2:
            return unhex(self.command[:2])
        else:
            return 0

    @property
    def pid_int(self):
        if len(self.command) > 2:
            return unhex(self.command[2:])
        else:
            return 0

    # TODO: remove later
    @property
    def supported(self):
        debug("OBDCommand.supported is deprecated. Use OBD.supports() instead", True)
        return False

    def __call__(self, messages):

        # filter for applicable messages (from the right ECU(s))
        for_us = lambda m: self.ecu & m.ecu > 0
        messages = list(filter(for_us, messages))

        # guarantee data size for the decoder
        for m in messages:
            self.__constrain_message_data(m)

        # create the response object with the raw data recieved
        # and reference to original command
        r = OBDResponse(self, messages)
        if messages:
            r.value, r.unit = self.decode(messages)

        return r


    def __constrain_message_data(self, message):
        """ pads or chops the data field to the size specified by this command """
        if self.bytes > 0:
            if len(message.data) > self.bytes:
                # chop off the right side
                message.data = message.data[:self.bytes]
            else:
                # pad the right with zeros
                message.data += (b'\x00' * (self.bytes - len(message.data)))


    def __str__(self):
        return "%s: %s" % (self.command, self.desc)

    def __hash__(self):
        # needed for using commands as keys in a dict (see async.py)
        return hash(self.command)

    def __eq__(self, other):
        if isinstance(other, OBDCommand):
            return (self.command == other.command)
        else:
            return False
