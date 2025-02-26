# Copyright the RTMPy Project
#
# RTMPy is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# RTMPy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with RTMPy.  If not, see <http://www.gnu.org/licenses/>.

"""
RTMP message implementations.
"""

from zope.interface import Interface, implements
import pyamf

from rtmpy.util import add_to_class


#: Changes the frame size for the RTMP stream
FRAME_SIZE = 0x01
# 0x02 is unknown
#: Send every x bytes read by both sides
BYTES_READ = 0x03
#: A stream control message, has subtypes
CONTROL = 0x04
#: The servers downstream bandwidth
DOWNSTREAM_BANDWIDTH = 0x05
#: The clients upstream bandwidth
UPSTREAM_BANDWIDTH = 0x06
#: Packet containing audio
# 0x07 anyone?
AUDIO_DATA = 0x08
#: Packet containing video data
VIDEO_DATA = 0x09
# 0x0a - 0x0e is unknown
#: Shared object with variable length
FLEX_SHARED_OBJECT = 0x10
#: Shared message with variable length
FLEX_MESSAGE = 0x11
#: An invoke which does not expect a reply
NOTIFY = 0x12
#: Has subtypes
SHARED_OBJECT = 0x13
#: Like remoting call, used for stream actions too
INVOKE = 0x14
# 0x15 anyone?
#: FLV data
FLV_DATA = 0x16


@add_to_class
def set_type(locals, type):
    """
    Assigns the message type to the locals of the defined class.
    """
    locals['__data_type__'] = type



class BaseError(Exception):
    """
    Base error class for all things C{message}.
    """



class DecodeError(BaseError):
    """
    Base error class for decoding RTMP messages.
    """



class TrailingDataError(DecodeError):
    """
    Raised if decoding a message does not consume the whole buffer.
    """



class EncodeError(BaseError):
    """
    Base error class for encoding RTMP messages.
    """



class UnknownType(BaseError):
    """
    Raised if an unknown message type is found.
    """



class IMessage(Interface):
    """
    An RTMP message in all its forms.

    @see: U{RTMP datatypes on OSFlash<http://osflash.org/documentation/
        rtmp#rtmp_datatypes>}
    """


    def encode(buffer):
        """
        Encodes the event instance to C{stream}.

        @type buffer: L{pyamf.util.BufferedByteStream}
        """


    def decode(buffer):
        """
        Decodes the event instance from C{stream}.

        @type buffer: L{pyamf.util.BufferedByteStream}
        """


    def dispatch(listener, timestamp):
        """
        Dispatch the event to the listener. Calls the correct method with the
        correct args according to L{IEventListener}.

        @param listener: Receives the event dispatch request.
        @type listener: L{IEventListener}
        @param timestamp: The timestamp that this message was dispatched.
        """



class IMessageListener(Interface):
    """
    Receives dispatched messages.
    """


    def onInvoke(invoke, timestamp):
        """
        Called when an invoke event have been received.

        @param invoke: The object representing the call request. See
            L{rtmpy.rtmp.event.Invoke} for an example implementation.
        @param timestamp: The timestamp that this message was dispatched.
        """


    def onNotify(notify, timestamp):
        """
        Similar to L{onInvoke} but no response is expected and will be ignored.

        @param notify: The object representing the notify request.
        @param timestamp: The timestamp that this message was dispatched.
        """


    def onAudioData(data, timestamp):
        """
        Called when audio data is received.

        @param data: The audio bytes received.
        @param timestamp: The timestamp that this message was dispatched.
        """


    def onVideoData(data, timestamp):
        """
        Called when video data is received.

        @param data: The video bytes received.
        @param timestamp: The timestamp that this message was dispatched.
        """

    # These methods should only be called on the RTMP command stream.

    def onFrameSize(size, timestamp):
        """
        Called when the RTMP frame size has changed.

        @param size: The new size of any subsequent RTMP frames in the stream.
        @param timestamp: The timestamp that this message was dispatched.
        """


    def onBytesRead(bytes, timestamp):
        """
        Called when the peer reports the number of raw bytes read from the
        stream. This is a kind of 'keep-alive' packet.

        @param bytes: The number of bytes read.
        @type bytes: C{int}
        @param timestamp: The timestamp that this message was dispatched.
        """


    def onControlMessage(message, timestamp):
        """
        Called when a control message is received by the peer.

        This could probably be split out into constituent parts once we
        understand what the various messages actually mean.

        @param message: The received message.
        @type message: L{rtmpy.rtmp.event.ControlMessage}
        @param timestamp: The timestamp that this message was dispatched.
        """


    def onDownstreamBandwidth(bandwidth, timestamp):
        """
        Called when the connected endpoint reports its downstream bandwidth
        limit.

        @param bandwidth: The amount of bandwidth available (appears to be
            measured in Kbps).
        @type bandwidth: C{int}
        @param timestamp: The timestamp that this message was dispatched.
        """


    def onUpstreamBandwidth(bandwidth, extra, timestamp):
        """
        Called when the connected endpoint reports its upstream bandwidth
        limit.

        @param bandwidth: The amount of bandwidth available (it appears to be
            measured in Kbps).
        @type bandwidth: C{int}
        @param extra: Not quite sure what this represents atm.
        @type extra: C{int}
        @param timestamp: The timestamp that this message was dispatched.
        """



class IMessageSender(Interface):
    """
    Indicates the ability to send a message.
    """


    def sendMessage(msg):
        """
        Sends a message to the receiving endpoint.

        @param msg: The message to send.
        @type msg: L{IMessage}
        @return: C{None}
        """



class Message(object):
    """
    An abstract class that all message types extend.
    """

    implements(IMessage)


    def encode(self, buf):
        """
        Called to encode the event to C{buf}.

        @type buf: L{pyamf.util.BufferedByteStream}
        """
        raise NotImplementedError


    def decode(self, buf):
        """
        Called to decode the event from C{buf}.

        @type buf: L{pyamf.util.BufferedByteStream}
        """
        raise NotImplementedError


    def dispatch(self, listener, timestamp):
        """
        Called to dispatch the event into listener.

        @type listener: L{IEventListener}
        """
        raise NotImplementedError


    def __repr__(self):
        t = self.__class__
        keys = self.__dict__.keys()
        keys = sorted(keys)

        s = '<%s.%s '

        for k in keys:
            s += '%s=%r ' % (k, self.__dict__[k])

        s += 'at 0x%x>'

        return s % (t.__module__, t.__name__, id(self))



class FrameSize(Message):
    """
    A frame size message. This determines the maximum number of bytes for the
    frame body in the RTMP stream.

    @ivar size: Number of bytes for RTMP frame bodies.
    @type size: C{int}
    """

    set_type(FRAME_SIZE)


    def __init__(self, size=None):
        self.size = size


    def decode(self, buf):
        """
        Decode a frame size message.
        """
        self.size = buf.read_ulong()


    def encode(self, buf):
        """
        Encode a frame size message.
        """
        if self.size is None:
            raise EncodeError('Frame size not set')

        try:
            buf.write_ulong(self.size)
        except TypeError:
            raise EncodeError('Frame size wrong type '
                '(expected int, got %r)' % (type(self.size),))


    def dispatch(self, listener, timestamp):
        """
        Dispatches the message to the listener.
        """
        listener.onFrameSize(self.size, timestamp)



class BytesRead(Message):
    """
    A bytes read message.

    @param bytes: The number of bytes read.
    @type bytes: C{int}
    """

    set_type(BYTES_READ)

    FOUR_GB_THRESHOLD = 0xee800000


    def __init__(self, bytes=None):
        self.bytes = bytes


    def decode(self, buf):
        """
        Decode a bytes read message.
        """
        self.bytes = buf.read_ulong()


    def encode(self, buf):
        """
        Encode a bytes read message.
        """
        if self.bytes is None:
            raise EncodeError('Bytes read not set')

        try:
            buf.write_ulong(self.bytes % self.FOUR_GB_THRESHOLD)
        except TypeError:
            raise EncodeError('Bytes read wrong type '
                '(expected int, got %r)' % (type(self.bytes),))


    def dispatch(self, listener, timestamp):
        """
        Dispatches the message to the listener.
        """
        listener.onBytesRead(self.bytes, timestamp)



class ControlMessage(Message):
    """
    A control message. Akin to Red5's Ping event.
    """

    set_type(CONTROL)

    UNDEFINED = -1
    PING = 6
    PONG = 7


    def __init__(self, type=None, value1=0, value2=None, value3=None):
        self.type = type
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3


    def decode(self, buf):
        """
        Decode a control message.
        """
        self.type = buf.read_short()
        self.value1 = buf.read_long()

        try:
            self.value2 = buf.read_long()
            self.value3 = buf.read_long()
        except IOError:
            pass


    def encode(self, buf):
        """
        Encode a control message.
        """
        if self.type is None:
            raise EncodeError('Type not set')

        try:
            buf.write_short(self.type)
        except TypeError:
            raise EncodeError('TypeError encoding type '
                '(expected int, got %r)' % (type(self.type),))

        try:
            buf.write_long(self.value1)
        except TypeError:
            raise EncodeError('TypeError encoding value1 '
                '(expected int, got %r)' % (type(self.value1),))

        if self.value2 is not None:
            try:
                buf.write_long(self.value2)
            except TypeError:
                raise EncodeError('TypeError encoding value2 '
                    '(expected int, got %r)' % (type(self.value2),))

        if self.value3 is not None:
            try:
                buf.write_long(self.value3)
            except TypeError:
                raise EncodeError('TypeError encoding value3 '
                    '(expected int, got %r)' % (type(self.value3),))


    def dispatch(self, listener, timestamp):
        """
        Dispatches the event to the listener.
        """
        return listener.onControlMessage(self, timestamp)



class DownstreamBandwidth(Message):
    """
    A downstream bandwidth message.
    """

    set_type(DOWNSTREAM_BANDWIDTH)


    def __init__(self, bandwidth=None):
        self.bandwidth = bandwidth


    def decode(self, buf):
        """
        Decode a downstream bandwidth message.
        """
        self.bandwidth = buf.read_ulong()


    def encode(self, buf):
        """
        Encode a downstream bandwidth message.
        """
        if self.bandwidth is None:
            raise EncodeError('Downstream bandwidth not set')

        try:
            buf.write_ulong(self.bandwidth)
        except TypeError:
            raise EncodeError('TypeError for downstream bandwidth '
                '(expected int, got %r)' % (type(self.bandwidth),))


    def dispatch(self, listener, timestamp):
        """
        Dispatches the message to the listener.
        """
        return listener.onDownstreamBandwidth(self.bandwidth, timestamp)



class UpstreamBandwidth(Message):
    """
    An upstream bandwidth message.

    @param bandwidth: The upstream bandwidth available.
    @type bandwidth: C{int}
    @param extra: Not sure what this is supposed to represent at the moment.
    """

    set_type(UPSTREAM_BANDWIDTH)


    def __init__(self, bandwidth=None, extra=None):
        self.bandwidth = bandwidth
        self.extra = extra


    def decode(self, buf):
        """
        Decode an upstream bandwidth message.
        """
        self.bandwidth = buf.read_ulong()
        self.extra = buf.read_uchar()


    def encode(self, buf):
        """
        Encode an upstream bandwidth message.
        """
        if self.bandwidth is None:
            raise EncodeError('Upstream bandwidth not set')

        if self.extra is None:
            raise EncodeError('Extra not set')

        try:
            buf.write_ulong(self.bandwidth)
        except TypeError:
            raise EncodeError('TypeError: Upstream bandwidth '
                '(expected int, got %r)' % (type(self.bandwidth),))

        try:
            buf.write_uchar(self.extra)
        except TypeError:
            raise EncodeError('TypeError: extra '
                '(expected int, got %r)' % (type(self.extra),))


    def dispatch(self, listener, timestamp):
        """
        Dispatches the message to the listener.
        """
        return listener.onUpstreamBandwidth(
            self.bandwidth, self.extra, timestamp)



class Notify(Message):
    """
    A notification message.

    @param name: The method name to call.
    @type name: C{str}
    @param args: A list of method arguments.
    """

    set_type(NOTIFY)


    def __init__(self, name=None, *args):
        self.name = name
        self.argv = list(args)


    def decode(self, buf):
        """
        Decode a notification message.
        """
        decoder = pyamf.get_decoder(pyamf.AMF0, stream=buf)

        self.name = decoder.next()
        self.argv = []
        while 1:
            try:
                x = decoder.next()
                self.argv.append(x)
            except StopIteration:
                break
            except UnicodeDecodeError:
                break



    def encode(self, buf):
        """
        Encode a notification message.
        """
        args = [self.name] + self.argv

        encoder = pyamf.get_encoder(pyamf.AMF0, buf)

        for a in args:
            encoder.writeElement(a)


    def dispatch(self, listener, timestamp):
        """
        Dispatches the message to the listener.
        """
        return listener.onNotify(self.name, self.argv, timestamp)



class Invoke(Message):
    """
    Similar to L{Notify} but a reply is expected.
    """

    set_type(INVOKE)

    encoding = pyamf.AMF0


    def __init__(self, name=None, id=None, *args):
        self.name = name
        self.id = id
        self.argv = list(args)


    def decode(self, buf):
        """
        Decode a notification message.
        """
        decoder = pyamf.get_decoder(self.encoding, stream=buf)

        self.name = decoder.next()
        self.id = decoder.next()
        self.argv = list(decoder)


    def encode(self, buf):
        """
        Encode a notification message.
        """
        args = [self.name, self.id] + self.argv

        encoder = pyamf.get_encoder(self.encoding, buf)

        for a in args:
            encoder.writeElement(a)


    def dispatch(self, listener, timestamp):
        """
        Dispatches the message to the listener.
        """
        listener.onInvoke(self.name, self.id, self.argv, timestamp)



class FlexMessage(Invoke):
    """
    The name is crap .. but basically its an Invoke but using amf3 to do the
    encoding/decoding.
    """

    set_type(FLEX_MESSAGE)

    encoding = pyamf.AMF3

    def decode(self, buf):
        if buf.peek(1) == '\x00':
            buf.seek(1, 1)
            self.encoding = pyamf.AMF0

        return Invoke.decode(self, buf)



class StreamingMessage(Message):
    """
    An message containing streaming data.

    @param data: The streaming data.
    @type data: C{str}
    """


    def __init__(self, data=None):
        self.data = data


    def decode(self, buf):
        """
        Decode a streaming message.
        """
        try:
            self.data = buf.read()
        except IOError:
            self.data = ''


    def encode(self, buf):
        """
        Encode a streaming message.
        """
        if self.data is None:
            raise EncodeError('No data set')

        try:
            buf.write(self.data)
        except TypeError:
            raise EncodeError('TypeError: data (expected str, got %r)' % (
                type(self.data),))



class AudioData(StreamingMessage):
    """
    A message containing audio data.
    """

    set_type(AUDIO_DATA)


    def dispatch(self, listener, timestamp):
        """
        Dispatches the message to the listener.
        """
        listener.onAudioData(self.data, timestamp)



class VideoData(StreamingMessage):
    """
    A message containing video data.
    """

    set_type(VIDEO_DATA)


    def dispatch(self, listener, timestamp):
        """
        Dispatches the message to the listener.
        """
        return listener.onVideoData(self.data, timestamp)



#: Map event types to event classes
TYPE_MAP = {}

for k, v in globals().items():
    try:
        if not IMessage.implementedBy(v):
            continue
    except TypeError:
        continue

    t = getattr(v, '__data_type__', None)

    if not t:
        continue

    TYPE_MAP[t] = v
    TYPE_MAP[v] = t

del k, v



def classByType(datatype):
    """
    A helper method that returns the mapped event class to the supplied
    datatype.

    @param datatype: The event type
    @type datatype: C{int}
    @return: The event class that is mapped to C{datatype}.
    @rtype: C{class} implementing L{interfaces.IMessage} for the given event
        type.
    @raise UnknownEventType: Unknown event type for C{datatype}.
    """
    try:
        return TYPE_MAP[datatype]
    except KeyError:
        raise UnknownType('Unknown event type %r' % (datatype,))



def typeByClass(obj):
    """
    Returns the message type based on C{obj}. C{obj} can be an instance of a
    class or a class object.

    If no message type is linked to C{obj}, B{-1} is returned.
    """
    try:
        return TYPE_MAP[obj]
    except KeyError:
        pass

    cls = getattr(obj, '__class__', None)

    if cls is None:
        return -1

    try:
        return TYPE_MAP[cls]
    except KeyError:
        pass

    return -1
