package ch.ethz.asl.kunicola.request;

import java.nio.ByteBuffer;
import java.util.LinkedHashMap;
import java.util.Map;

import ch.ethz.asl.kunicola.util.ServerMessage;

public class MultiGetRequest extends GetRequest {

	private static final int MAX_NUMBER_KEYS = 10;

	private final boolean readSharded;
	private final int[] serverIds;

	private Map<Integer, byte[]> responseMap;

	public MultiGetRequest(byte[] content, int serverId, int numberOfServers) {
		super(content, serverId, "mget", numberOfServers);
		this.readSharded = false;
		this.serverIds = null;
	}

	public MultiGetRequest(byte[] content, int[] serverIds, int numberOfServers) {
		super(content, "mget", numberOfServers);
		this.readSharded = true;
		this.serverIds = serverIds;
	}

	@Override
	public ServerMessage[] getServerMessages() {
		if (!readSharded) { // non-sharded -> just perform normal get request
			return super.getServerMessages();
		}

		ServerMessage[] msgs = new ServerMessage[this.serverIds.length];
		responseMap = new LinkedHashMap<>(serverIds.length);

		// extract number of keys
		byte[] content = getContent();
		this.keyCount = 0;

		int[] separatorIdx = new int[MAX_NUMBER_KEYS + 1];
		for (int i = 0; i < content.length; i++) {
			if (content[i] == ' ') {
				separatorIdx[keyCount] = i;
				this.keyCount++;
			}
		}
		separatorIdx[keyCount] = content.length - 2;

		// calculate load per server
		int baseNumberOfKeysPerServer = keyCount / serverIds.length;
		int numberOfRemainingKeys = keyCount % serverIds.length;

		int keyIdx = 0;
		int msgIdx = 0;

		// create partial msg for each server
		for (int serverId : serverIds) {
			responseMap.put(serverId, null);

			int numberOfKeys = baseNumberOfKeysPerServer;
			if (numberOfRemainingKeys > 0) {
				numberOfKeys++;
				numberOfRemainingKeys--;
			}

			int start = separatorIdx[keyIdx] + 1;
			int end = separatorIdx[keyIdx + numberOfKeys];

			int msgContentSize = 4 + end - start + 2; // "get " takes 4b and "\r\n" takes 2b
			byte[] msgContent = new byte[msgContentSize];

			// init static partial msg content
			msgContent[0] = 'g';
			msgContent[1] = 'e';
			msgContent[2] = 't';
			msgContent[3] = ' ';
			msgContent[msgContentSize - 2] = '\r';
			msgContent[msgContentSize - 1] = '\n';

			// copy bytes into partial msg
			for (int i = start, j = 4; i < end; i++, j++) {
				msgContent[j] = content[i];
			}

			msgs[msgIdx] = new ServerMessage(serverId, msgContent);

			keyIdx += numberOfKeys;
			msgIdx++;
		}
		return msgs;
	}

	@Override
	public boolean putServerResponse(Integer serverId, ByteBuffer buffer) {
		boolean isResponseComplete = super.putServerResponse(serverId, buffer);

		if (!readSharded || !isResponseComplete) { // non-sharded -> just perform normal get request
			return isResponseComplete;
		}

		// store the partial response
		buffer.position(buffer.position() - 5); // ignore END\r\n
		buffer.flip();
		byte[] dst = new byte[buffer.remaining()];

		buffer.get(dst);
		responseMap.put(serverId, dst);

		// check if all server already completed the request
		if (responseMap.containsValue(null)) {
			return false;
		}

		// assemble the client response by merging the partial responses
		buffer.clear();
		for (byte[] partialResponse : responseMap.values()) {
			buffer.put(partialResponse);
		}
		buffer.put(RESPONSE_END_MARKER);

		setClientResponseBuffer(buffer);
		return true;
	}
}
