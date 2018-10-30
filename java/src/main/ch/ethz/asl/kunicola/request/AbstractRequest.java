package ch.ethz.asl.kunicola.request;

import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.nio.charset.CharsetDecoder;

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
	private long processStartTime;
	private long enqueueTime;
	private long dequeueTime;
	private long[] serverStartTime; // indexed by server id
	private long[] serverEndTime; // indexed by server id
	private long processEndTime;
	protected int keyCount = 0;
	protected int hitCount = 0;

	public AbstractRequest(byte[] content, String type, int numberOfServers) {
		super();
		this.setContent(content);
		this.type = type;
		this.numberOfServers = numberOfServers;

		serverStartTime = new long[numberOfServers];
		serverEndTime = new long[numberOfServers];
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

	public int getNumberOfServers() {
		return numberOfServers;
	}

	public int getKeyCount() {
		return keyCount;
	}

	public int getHitCount() {
		return hitCount;
	}

	public long getProcessStartTime() {
		return processStartTime;
	}

	public void setProcessStartTime(long processStartTime) {
		this.processStartTime = processStartTime;
	}

	public long getEnqueueTime() {
		return enqueueTime;
	}

	public void setEnqueueTime(long enqueueTime) {
		this.enqueueTime = enqueueTime;
	}

	public long getDequeueTime() {
		return dequeueTime;
	}

	public void setDequeueTime(long dequeueTime) {
		this.dequeueTime = dequeueTime;
	}

	public long[] getServerStartTime() {
		return serverStartTime;
	}

	public void setServerStartTime(int serverId, long serverStartTime) {
		this.serverStartTime[serverId] = serverStartTime;
	}

	public long[] getServerEndTime() {
		return serverEndTime;
	}

	public void setServerEndTime(int serverId, long serverEndTime) {
		this.serverEndTime[serverId] = serverEndTime;
	}

	public long getProcessEndTime() {
		return processEndTime;
	}

	public void setProcessEndTime(long processEndTime) {
		this.processEndTime = processEndTime;
	}

	public void setKeyCount(int keyCount) {
		this.keyCount = keyCount;
	}

	public void setHitCount(int hitCount) {
		this.hitCount = hitCount;
	}

}
