package ch.ethz.asl.kunicola;

import java.nio.ByteBuffer;
import java.util.LinkedList;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class BufferPool { // TODO [nku] test performance of direct buffers

	private final static Logger logger = LogManager.getLogger();
	private static final int BUFFER_SIZE = 1024;
	private static final int POOL_LIMIT = 100; // TODO [nku] think about if this is problematic

	private static LinkedList<ByteBuffer> pool = new LinkedList<>();

	// currently can only be used from single thread (net thread)
	public static ByteBuffer getBuffer() {
		ByteBuffer buffer;
		if (pool.isEmpty()) {
			logger.info("BufferPool is Empty -> Allocating new Buffer");
			buffer = ByteBuffer.allocate(BUFFER_SIZE);
		} else {
			buffer = pool.removeLast();
		}
		buffer.clear();
		return buffer;
	}

	public static void putBuffer(ByteBuffer buffer) {
		if (pool.size() < POOL_LIMIT) {
			pool.addLast(buffer);
		} else {
			logger.info("BufferPool is Full -> Buffer Discarded");
		}
	}
}
