package ch.ethz.asl.kunicola.request;

import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.nio.charset.CharsetDecoder;
import java.time.Instant;
import java.util.Arrays;
import java.util.stream.Collectors;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.util.DecoderUtil;
import ch.ethz.asl.kunicola.util.ServerMessage;

public abstract class AbstractRequest {

    private final static Logger LOG = LogManager.getLogger();
    final static CharsetDecoder DECODER = Charset.forName("UTF8").newDecoder();

    private SocketChannel clientSocketChannel;
    private byte[] content;
    private ByteBuffer clientResponseBuffer;
    private final String type;
    private final int numberOfServers;

    // Stats
    private Instant processStartTime;
    private Instant enqueueTime;
    private Instant dequeueTime;
    private Instant[] serverStartTime; // indexed by server id
    private Instant[] serverEndTime; // indexed by server id
    private Instant processEndTime;
    protected int keyCount = 0;
    protected int hitCount = 0;

    public AbstractRequest(byte[] content, String type, int numberOfServers) {
	super();
	this.setContent(content);
	this.type = type;
	this.numberOfServers = numberOfServers;

	serverStartTime = new Instant[numberOfServers];
	serverEndTime = new Instant[numberOfServers];
    }

    public abstract ServerMessage[] getServerMessages();

    public abstract boolean putServerResponse(Integer serverId, ByteBuffer byteBuffer);

    public ByteBuffer getClientResponseBuffer() {
	return clientResponseBuffer;
    }

    public void setClientResponseBuffer(ByteBuffer clientResponseBuffer) {
	this.clientResponseBuffer = clientResponseBuffer;
    }

    public SocketChannel getClientSocketChannel() {
	return clientSocketChannel;
    }

    public void setClientSocketChannel(SocketChannel clientSocketChannel) {
	this.clientSocketChannel = clientSocketChannel;
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
	    return type;
	}
    }

    public String getType() {
	return type;
    }

    public Instant getProcessStartTime() {
	return processStartTime;
    }

    public void setProcessStartTime(Instant processStartTime) {
	this.processStartTime = processStartTime;
    }

    public Instant getEnqueueTime() {
	return enqueueTime;
    }

    public void setEnqueueTime(Instant enqueueTime) {
	this.enqueueTime = enqueueTime;
    }

    public Instant getDequeueTime() {
	return dequeueTime;
    }

    public void setDequeueTime(Instant dequeueTime) {
	this.dequeueTime = dequeueTime;
    }

    public Instant[] getServerStartTime() {
	return serverStartTime;
    }

    public Instant getServerStartTime(int serverId) {
	return serverStartTime[serverId];
    }

    public void setServerStartTime(int serverId, Instant serverStartTime) {
	this.serverStartTime[serverId] = serverStartTime;
    }

    public void setServerStartTime(Instant[] serverStartTime) {
	this.serverStartTime = serverStartTime;
    }

    public Instant[] getServerEndTime() {
	return serverEndTime;
    }

    public Instant getServerEndTime(int serverId) {
	return serverEndTime[serverId];
    }

    public String getFormattedServerStartTime() {
	return Arrays.stream(serverStartTime)
		.map(x -> Long.toString(x.toEpochMilli()))
		.collect(Collectors.joining(","));
    }

    public String getFormattedServerEndTime() {
	return Arrays.stream(serverEndTime)
		.map(x -> Long.toString(x.toEpochMilli()))
		.collect(Collectors.joining(","));
    }

    public void setServerEndTime(int serverId, Instant serverEndTime) {
	this.serverEndTime[serverId] = serverEndTime;
    }

    public Instant getProcessEndTime() {
	return processEndTime;
    }

    public void setProcessEndTime(Instant processEndTime) {
	this.processEndTime = processEndTime;
    }

    public int getNumberOfServers() {
	return numberOfServers;
    }

    public int getKeyCount() {
	return keyCount;
    }

    public int getHitCount() {
	return hitCount;
    }

}
