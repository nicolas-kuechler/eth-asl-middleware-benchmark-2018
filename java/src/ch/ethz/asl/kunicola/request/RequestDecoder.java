package ch.ethz.asl.kunicola.request;

import java.nio.ByteBuffer;

// TODO [nku] add JUnit tests
public class RequestDecoder {

    private boolean readSharded = false;
    private int numberOfServers;
    private int nextRoundRobinServerId = 0;

    public AbstractRequest decode(ByteBuffer buffer) {
	boolean g0 = buffer.get(0) == 'g';
	boolean s0 = buffer.get(0) == 's';
	boolean e1 = buffer.get(1) == 'e';
	boolean t2 = buffer.get(2) == 't';

	int pos = buffer.position();
	boolean endsWithNewLine = buffer.get(pos - 2) == '\r' &&
		buffer.get(pos - 1) == '\n';

	AbstractRequest request = null;
	byte[] content;

	if (s0 && e1 && t2 && endsWithNewLine) { // SET Request
	    buffer.flip();
	    int whitespaceCount = 0;
	    int bytes = 0;
	    while (buffer.hasRemaining()) {
		byte b = buffer.get();

		if (whitespaceCount == 4 && b != ' ' && b != '\r') {
		    // read <bytes>
		    int digit = (int) ((char) b) - (int) '0';
		    bytes *= 10;
		    bytes += digit;
		}
		if (b == ' ') {
		    whitespaceCount++;
		} else if (b == '\r') {
		    break;
		}
	    }

	    if (buffer.limit() == bytes + buffer.position() + 3) {
		// SET Request Complete
		buffer.position(pos);
		buffer.flip();
		content = new byte[buffer.remaining()];
		buffer.get(content);
		request = new SetRequest(content, numberOfServers);
	    }

	} else if (g0 && e1 && t2 && endsWithNewLine) { // Get or MultiGet Request
	    buffer.flip();
	    int whitespaceCount = 0;
	    while (buffer.hasRemaining() && (whitespaceCount < 2 || whitespaceCount < numberOfServers)) {
		if (buffer.get() == ' ') {
		    whitespaceCount++;
		}
	    }
	    buffer.position(pos);
	    buffer.flip();
	    content = new byte[buffer.remaining()];
	    buffer.get(content);
	    if (whitespaceCount < 2) { // GET Request
		request = new GetRequest(content, getRoundRobinServerId(), numberOfServers);
	    } else {// MULTI GET Request
		if (readSharded) {
		    int serverIds[] = getRoundRobinServerIds(whitespaceCount);
		    request = new MultiGetRequest(content, serverIds, numberOfServers);
		} else {
		    request = new MultiGetRequest(content, getRoundRobinServerId(), numberOfServers);
		}

	    }
	}

	return request;
    }

    private int getRoundRobinServerId() {
	int serverId = nextRoundRobinServerId;
	nextRoundRobinServerId = (nextRoundRobinServerId + 1) % numberOfServers;
	return serverId;
    }

    private int[] getRoundRobinServerIds(int number) {
	int[] serverIds = new int[number];

	for (int i = 0; i < number; i++) {
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

}
