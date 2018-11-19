package ch.ethz.asl.kunicola.util;

import java.nio.ByteBuffer;

public class BufferTimePair {

	private ByteBuffer buffer;
	private long time;

	public BufferTimePair(ByteBuffer buffer, long time) {
		this.buffer = buffer;
		this.time = time;
	}

	public ByteBuffer getBuffer() {
		return buffer;
	}

	public long getTime() {
		return time;
	}

}
