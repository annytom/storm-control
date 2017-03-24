#!/usr/bin/env python
"""
The messages that are passed between modules.

Hazen 01/17
"""

import storm_control.sc_library.halExceptions as halExceptions
import storm_control.sc_library.hdebug as hdebug


#
# This dictionary contains all of the valid message types. Modules
# may dynamically add to this dictionary using addMessage().
#
valid_messages = {
    
    # HAL/core/general messages.
    'add to ui' : True,
    'close event' : True,
    'configure1' : True,
    'configure2' : True,
    'current parameters' : True,
    'module' : True,
    'new directory' : True,
    'new parameters file' : True,
    'new shutters file' : True,
    'start' : True,
    'sync' : True
    }

def addMessage(name, check_exists = True):
    """
    Modules should call this function at initialization to add additional messages.
    """
    global valid_messages
    if check_exists and name in valid_messages:
        raise halExceptions.HalException("Message " + name + " already exists!")
    valid_messages[name] = True


class HalMessageBase(object):
    """
    Base class for the HalMessage as well as for various response
    such as errors, warnings or data.
    """
    def __init__(self, m_type = "", source = None, **kwds):
        """
        m_type - String that defines the message type. This should be a space 
                 separated lower case string.

        source - HalModule object that sent the message.
        """
        super().__init__(**kwds)

        self.m_type = m_type
        self.source = source
        
    def getSource(self):
        return self.source

    def getSourceName(self):
        return self.source.module_name

    def getType(self):
        return self.m_type


class HalMessage(HalMessageBase):

    def __init__(self, data = None, sync = False, level = 1, finalizer = None, **kwds):
        """
        data - Python object containing the message data. In general this should
               be a dictionary or a Parameters object.

        sync - Boolean that indicates whether or not all the messages before
               this message should be processed before continuing to this message.

        level - Integer that for the message 'level'. Most messages are level 1
                but if the message is one that there will be a lot of, and that
                is only relevant to one or two other modules (such as commands
                from a USB joystick) then it should be some other level so that
                modules that are not interested can more quickly ignore it.

                Convention:
                 1. General messages
                 2. New frame messages
                 3. Joystick / mouse drag messages

        finalizer - A function with no arguments to call when the message has been 
                    processed by all of the modules.
        """
        super().__init__(**kwds)

        self.data = data
        self.finalizer = finalizer
        self.level = level
        self.m_errors = []
        self.responses = []
        self.sync = sync

        self.ref_count = 0

        # Log when message was created.
        if (self.level == 1):
            self.logEvent("created")

    def addError(self, hal_message_error):
        self.m_errors.append(hal_message_error)

    def addResponse(self, hal_message_response):
        self.responses.append(hal_message_response)
        
    def finalize(self):

        # Log when message was destroyed.
        if (self.level == 1):
            self.logEvent("destroyed")

        if self.finalizer is not None:
            self.finalizer()

    def getData(self):
        return self.data

    def getErrors(self):
        return self.m_errors

    def getResponses(self):
        return self.responses

    def hasErrors(self):
        return len(self.m_errors) > 0

    def hasResponses(self):
        return len(self.responses) > 0

    def logEvent(self, event_name):
        hdebug.logText(",".join([event_name, str(id(self)), self.source.module_name, self.m_type]))


class HalMessageError(object):
    """
    If a module has a problem with a message that it can't handle then
    it should call the message's addError() method with one of these objects.
    """
    def __init__(self, source = "", message = "", m_exception = None, **kwds):
        """
        source - The halmodule that created the error/warning as a string.
        message - The warning / error message as a string.
        m_exception - The exception for the source to raise if can't handle
                      this error. If this is not set then we'll just get a
                      warning.
        """
        super().__init__(**kwds)

        self.message = message
        self.m_exception = m_exception
        self.source = source

    def getException(self):
        return self.m_exception
    
    def hasException(self):
        return self.m_exception is not None


class HalMessageResponse(object):
    """
    If a module wants to send some information back to the message sender then
    it should call the message's addResponse() method with one of the objects.
    """
    def __init__(self, source = "", data = None, **kwds):
        """
        source - The halmodule that added the response as a string.
        data - Python object containing the response.
        """
        super().__init__(**kwds)

        self.data = data
        self.source = source

    def getData(self):
        return self.data


class SyncMessage(HalMessage):
    """
    A message whose sole purpose is to jam up the queue until 
    everything before it is processed. Use sparingly..
    """
    def __init__(self, source):
        kwds = {"m_type" : "sync",
                "source" : source,
                "sync" : True}
        super().__init__(**kwds)
        
#
# The MIT License
#
# Copyright (c) 2017 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#