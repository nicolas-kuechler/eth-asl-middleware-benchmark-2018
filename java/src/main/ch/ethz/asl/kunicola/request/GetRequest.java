package ch.ethz.asl.kunicola.request;

import java.nio.ByteBuffer;

import ch.ethz.asl.kunicola.util.ServerMessage;

public class GetRequest extends AbstractRequest {

	protected static final byte[] RESPONSE_END_MARKER = "END\r\n".getBytes();
	private final int serverId;

	public GetRequest(byte[] content, int serverId, int numberOfServers) {
		super(content, "get", numberOfServers);
		this.serverId = serverId;
		this.keyCount = 1;
	}

	public GetRequest(byte[] content, int serverId, String type, int numberOfServers) {
		super(content, type, numberOfServers);
		this.serverId = serverId;
	}

	protected GetRequest(byte[] content, String type, int numberOfServers) {
		super(content, type, numberOfServers);
		serverId = -1;
	}

	@Override
	public ServerMessage[] getServerMessages() {
		return new ServerMessage[] { new ServerMessage(serverId, getContent()) };
	}

	@Override
	public boolean putServerResponse(Integer serverId, ByteBuffer buffer) {
		buffer.position(buffer.position() - RESPONSE_END_MARKER.length);

		boolean isComplete = true;

		for (int i = 0; i < RESPONSE_END_MARKER.length; i++) {
			if (buffer.get() != RESPONSE_END_MARKER[i]) {
				isComplete = false;
			}
		}

		if (isComplete) {

			buffer.flip();
			int whitespaceCount = 0;
			int bytes = 0;

			while (buffer.hasRemaining()) {
				byte b = buffer.get();
				if (whitespaceCount == 0 && b == 'V') {
					this.hitCount++; // increase hit count per value
				}

				if (whitespaceCount == 3 && b != ' ' && b != '\r') {
					// read <bytes>
					int digit = (int) ((char) b) - (int) '0';
					bytes *= 10;
					bytes += digit;
				} else if (whitespaceCount == 3) {
					// jump over data block such that the next char should be the \n
					buffer.position(buffer.position() + bytes + 1);
					whitespaceCount = 0; // reset whitespace count
					bytes = 0;
				}
				if (b == ' ') {
					whitespaceCount++;
				}
			}

			setClientResponseBuffer(buffer);

		}

		return isComplete;
	}

}
