import io
import struct

def coro(listener):
    buffer = io.BytesIO()
    buffersize = 0
    waitingForSize = True
    chunkbuffer = io.BytesIO()
    chunksize = 0
    l = 0
    listener.send(None)
    while True:
        if waitingForSize:
            while chunksize < 4:
                chunk = yield
                chunksize = chunksize + len(chunk)
                chunkbuffer.write(chunk)
            x = chunkbuffer.getvalue()
            (l,) = struct.unpack("!I", x[:4])
            buffer = io.BytesIO()
            buffer.write(x[4:])
            buffersize = chunksize - 4
            chunksize = 0
            waitingForSize = False
        else:
            while buffersize < l:
                chunk = yield
                buffer.write(chunk)
                buffersize = buffersize + len(chunk)
            v = buffer.getvalue()
            listener.send(v[:l])
            chunkbuffer = io.BytesIO()
            chunkbuffer.write(v[l:])
            chunksize = buffersize - l
            buffersize = 0
            waitingForSize = True

def listener():
    while True:
        x = yield
        print(x)

if __name__ == "__main__":
    msgs = [b"bajabongobajabongo", b"supercaligrafilistic"]
    ls = [len(msg) for msg in msgs]
    ss = io.BytesIO()
    for i, j in zip(ls, msgs):
        ss.write(struct.pack("!I", i))
        ss.write(j)
    ss.write(b"EOF")
    ssrepr = ss.getvalue()
    i = 0
    l = listener()
    producer = coro(l)
    producer.send(None)
    while True:
        v = ssrepr[i:i+5]
        producer.send(v)
        i = i + 5
        if len(v) < 5:
            break

