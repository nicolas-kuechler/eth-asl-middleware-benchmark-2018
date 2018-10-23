package ch.ethz.asl.kunicola.request;

import java.nio.ByteBuffer;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.util.DecoderUtil;
import ch.ethz.asl.kunicola.util.ServerMessage;

public class SetRequest extends AbstractRequest {

    private final static Logger LOG = LogManager.getLogger();
    private final static byte[] SUCCESS_MSG = "STORED\r\n".getBytes();

    private int responseCounter = 0;

    public SetRequest(byte[] content, int numberOfServers) {
	super(content, "set", numberOfServers);
    }

    @Override
    public ServerMessage[] getServerMessages() {
	int numberOfServers = getNumberOfServers();
	ServerMessage[] msgs = new ServerMessage[numberOfServers];

	for (int serverId = 0; serverId < numberOfServers; serverId++) {
	    msgs[serverId] = new ServerMessage(serverId, getContent());
	}

	return msgs;
    }

    @Override
    public boolean putServerResponse(Integer serverId, ByteBuffer buffer) {

	if (buffer.get(buffer.position() - 2) != '\r' || buffer.get(buffer.position() - 1) != '\n') {
	    LOG.debug("Incomplete Memcached server response");
	    return false; // server response for some reason not complete
	}

	responseCounter++;

	// parse the server response
	int pos = buffer.position();
	int i = 0;
	buffer.flip();
	while (buffer.hasRemaining()) {
	    byte b = buffer.get();
	    if (SUCCESS_MSG[i] != b) {
		buffer.position(pos);
		LOG.warn("Memcached server returned error msg, preparing for client relay: {}   ",
			DecoderUtil.decode(buffer)); // TODO [nku] do differently
		setClientResponseBuffer(buffer); // relay one of the error msgs
		break;
	    }
	    i++;
	}

	buffer.position(pos); // restore old position

	if (responseCounter == getNumberOfServers()) {

	    if (getClientResponseBuffer() == null) {
		setClientResponseBuffer(buffer);
	    }

	    return true;
	}

	return false;
    }

}
