package ch.ethz.asl.kunicola.request;

import java.nio.ByteBuffer;

public class MultiGetClientRequest extends GetRequest {

    private final boolean readSharded;

    public MultiGetClientRequest(byte[] content, int serverId, boolean readSharded) {
	super(content, serverId, "multi-get");
	this.readSharded = readSharded;
    }

    @Override
    public ServerMessage[] getServerMessages() {
	if (!readSharded) { // non-sharded -> just perform normal get request
	    return super.getServerMessages();
	}

	// TODO [nku] implement multi get
	throw new UnsupportedOperationException("MultiGetClientRequest: not implemented yet");
    }

    @Override
    public boolean putServerResponse(Integer serverId, ByteBuffer buffer) {
	if (!readSharded) { // non-sharded -> just perform normal get request
	    return super.putServerResponse(serverId, buffer);
	}
	// TODO [nku] implement multi get
	throw new UnsupportedOperationException("MultiGetClientRequest: not implemented yet");
    }

}
