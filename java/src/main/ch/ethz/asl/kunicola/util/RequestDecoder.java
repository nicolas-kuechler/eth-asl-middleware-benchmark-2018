package ch.ethz.asl.kunicola.util;

import java.nio.BufferUnderflowException;
import java.nio.ByteBuffer;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.request.GetRequest;
import ch.ethz.asl.kunicola.request.MultiGetRequest;
import ch.ethz.asl.kunicola.request.SetRequest;
import ch.ethz.asl.kunicola.request.UnknownRequest;

/**
 * Tries to decode a request from a byte buffer by parsing the cmd of the
 * request and checking that the request is complete. If the request is
 * complete, the necessary number of server id's are allocated to the request to
 * ensure round robin behaviour for load balancing between the different
 * servers. In case of an illegal/unknown request, the request is logged and a
 * dummy request returned.
 * 
 * @author nicolas-kuechler
 *
 */
public class RequestDecoder {

	private final static Logger LOG = LogManager.getLogger();

	private boolean readSharded = false;
	private int numberOfServers = 0;
	private int nextRoundRobinServerId = 0;

	boolean lastDecodedRequestContainsMore = false;

	/**
	 * decodes the buffer into a request
	 * 
	 * @param buffer
	 * @return GetRequest, MultiGetRequest or SetRequest when the buffer contained a
	 *         valid and complete request. UnknownRequest when the request is not
	 *         known and null when the request is not complete yet.
	 */
	public AbstractRequest decode(ByteBuffer buffer) {
		AbstractRequest request = null;
		boolean isCmdComplete = false;
		boolean isRequestComplete = false;
		lastDecodedRequestContainsMore = false;

		int initialPos = buffer.position();
		int initialLimit = buffer.limit();

		try {
			buffer.flip();
			byte b0 = buffer.get();
			if (b0 == 'g') { // GET or MGET COMMAND
				// FORMAT: get <key>*\r\n
				if (buffer.get() != 'e') throw new IllegalRequestException("get: expected e1");
				if (buffer.get() != 't') throw new IllegalRequestException("get: expected t2");
				if (buffer.get() != ' ') throw new IllegalRequestException("get: expected whitespace3");

				int keyCount = 0;

				// scanning over keys to the end of the command line
				while (buffer.hasRemaining() && !isCmdComplete) {
					byte b = buffer.get();
					if (b == ' ') {
						keyCount++; // whitespace indicates end of key
					} else if (b == '\r') {
						if (buffer.get() == '\n') {
							keyCount++; // \r\n indicates end of key and command line
							isCmdComplete = true;
						} else {
							throw new IllegalRequestException("get: expected \\n at the end of get command line");
						}
					} else if (b == '\n') {
						throw new IllegalRequestException("get: unexpected \\n in command line");
					}
				}

				// if get command is complete create the request
				if (isCmdComplete) {
					buffer.flip();
					byte[] content = new byte[buffer.remaining()];
					buffer.get(content);

					if (keyCount == 1) { // GET COMMAND
						request = new GetRequest(content, getRoundRobinServerId(), numberOfServers);
					} else if (readSharded) { // SHARDED MGET COMMAND
						request = new MultiGetRequest(content, getRoundRobinServerIds(keyCount), numberOfServers);
					} else { // NON-SHARDED MGET COMMAND
						request = new MultiGetRequest(content, getRoundRobinServerId(), numberOfServers);
					}
					isRequestComplete = true;
				}

			} else if (b0 == 's') { // SET COMMAND
				// FORMAT: set <key> <flags> <exptime> <bytes> [noreply]\r\n<data block>\r\n
				if (buffer.get() != 'e') throw new IllegalRequestException("set: expected e1");
				if (buffer.get() != 't') throw new IllegalRequestException("set: expected t2");
				if (buffer.get() != ' ') throw new IllegalRequestException("set: expected whitespace3");

				int whitespaceCount = 0;

				// skip over <key> <flags> <exptime> (3 whitespaces)
				while (buffer.hasRemaining() && whitespaceCount < 3) {
					byte b = buffer.get();
					if (b == ' ') whitespaceCount++;
					if (b == '\r' || b == '\n') {
						throw new IllegalRequestException("set: unexpected \\r \\n in command line");
					}
				}

				// extract <bytes>
				int bytes = 0;
				while (buffer.hasRemaining() && !isCmdComplete) {
					byte b = buffer.get();

					if (Character.isDigit((char) b)) { // within <bytes>
						int digit = (int) ((char) b) - (int) '0';
						bytes *= 10;
						bytes += digit;
					} else if (b == '\r') { // end of command line
						if (buffer.get() != '\n') {
							throw new IllegalRequestException("set: expected \\n at end of command line");
						}
						isCmdComplete = true;
					} else if (b == ' ') { // expect optional noreply
						if (buffer.get() != 'n') throw new IllegalRequestException("set: noreply expected n0");
						if (buffer.get() != 'o') throw new IllegalRequestException("set: noreply expected o1");
						if (buffer.get() != 'r') throw new IllegalRequestException("set: noreply expected r2");
						if (buffer.get() != 'e') throw new IllegalRequestException("set: noreply expected e3");
						if (buffer.get() != 'p') throw new IllegalRequestException("set: noreply expected p4");
						if (buffer.get() != 'l') throw new IllegalRequestException("set: noreply expected l5");
						if (buffer.get() != 'y') throw new IllegalRequestException("set: noreply expected y6");
						if (buffer.get() != '\r') throw new IllegalRequestException("set: noreply expected \\r7");
						if (buffer.get() != '\n') throw new IllegalRequestException("set: noreply expected \\nr8");
						isCmdComplete = true;
					} else {
						throw new IllegalRequestException("set: expected <bytes>");
					}
				}

				// calc if data block is complete
				int dataBlockEndPos = bytes + buffer.position();
				if (isCmdComplete && dataBlockEndPos + 2 <= buffer.limit()) {
					buffer.position(dataBlockEndPos); // move to datablock end and check that it ends with \r\n
					if (buffer.get() != '\r') {
						throw new IllegalRequestException("set: expected \\r at end-1 of datablock");
					}
					if (buffer.get() != '\n') {
						throw new IllegalRequestException("set: expected \\n at end of datablock");
					}

					buffer.flip();
					byte[] content = new byte[buffer.remaining()];
					buffer.get(content);
					request = new SetRequest(content, numberOfServers);
					isRequestComplete = true;
				}
			} else {
				throw new IllegalRequestException("unknown starting char, should be either s or g");
			}

		} catch (IllegalRequestException e) {
			boolean foundNewLine = false;
			LOG.debug("Potentially Incomplete IllegalRequestException: {}", e.getMessage());
			// for an illegal request discard everything until new line character
			while (buffer.hasRemaining() && !foundNewLine) {
				byte b = buffer.get();
				if (b == '\n') {
					buffer.flip();
					byte[] content = new byte[buffer.remaining()];
					buffer.get(content);
					request = new UnknownRequest(content, e.getMessage());
					LOG.warn("IllegalRequestException: Msg:{} Content:{}", e.getMessage(), DecoderUtil.decode(content));
					foundNewLine = true;
				}
			}
		} catch (BufferUnderflowException e) {
			LOG.error("BufferUnderflowException occured while decoding request: Clearing Buffer and Resetting Request");
			isRequestComplete = false;
			request = null;
			buffer.clear();
		}

		if (isRequestComplete && buffer.position() < initialPos) {
			int pos = buffer.position();
			buffer.limit(initialLimit);
			buffer.compact();
			buffer.position(initialPos - pos);
			lastDecodedRequestContainsMore = true;
		} else {
			// restore old position and limit
			buffer.limit(initialLimit);
			buffer.position(initialPos);
			lastDecodedRequestContainsMore = false;
		}

		return request;
	}

	private int getRoundRobinServerId() {
		int serverId = nextRoundRobinServerId;
		nextRoundRobinServerId = (nextRoundRobinServerId + 1) % numberOfServers;
		return serverId;
	}

	private int[] getRoundRobinServerIds(int keyCount) {
		int size = Math.min(keyCount, numberOfServers);
		int[] serverIds = new int[size];

		for (int i = 0; i < size; i++) {
			serverIds[i] = getRoundRobinServerId();
		}
		return serverIds;
	}

	public RequestDecoder withShardedMultiGet(boolean readSharded) {
		this.readSharded = readSharded;
		return this;
	}

	public RequestDecoder withNumberOfServers(int numberOfServers) {
		this.numberOfServers = numberOfServers;
		return this;
	}

	public boolean hasMore() {
		return lastDecodedRequestContainsMore;
	}

}
