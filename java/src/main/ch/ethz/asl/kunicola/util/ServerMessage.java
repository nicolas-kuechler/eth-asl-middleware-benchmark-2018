package ch.ethz.asl.kunicola.util;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class ServerMessage {

    final static Logger LOG = LogManager.getLogger();

    private int serverId;
    private byte[] content;

    public ServerMessage(int serverId, byte[] content) {
	super();
	this.serverId = serverId;
	this.content = content;
    }

    public int getServerId() {
	return serverId;
    }

    public void setServerId(int serverId) {
	this.serverId = serverId;
    }

    public byte[] getContent() {
	return content;
    }

    public void setContent(byte[] content) {
	this.content = content;
    }

    @Override
    public String toString() {
	if (LOG.isDebugEnabled()) {
	    return DecoderUtil.decode(getContent());
	} else {
	    return "";
	}
    }

}
