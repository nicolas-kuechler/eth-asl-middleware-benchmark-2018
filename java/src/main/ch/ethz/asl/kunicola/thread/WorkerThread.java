package ch.ethz.asl.kunicola.thread;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.concurrent.BlockingQueue;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.statistic.Statistic;
import ch.ethz.asl.kunicola.util.DecoderUtil;
import ch.ethz.asl.kunicola.util.ServerMessage;

public class WorkerThread extends Thread {

    private final Logger LOG = LogManager.getLogger();

    private static final int BUFFER_SIZE = 65536; // 2^16 b enough to handle up to ten 4096b values in multiget
    private static final int STATS_WINDOWS_SIZE = 5000; // ms

    private int id = -1;
    private BlockingQueue<AbstractRequest> queue = null;

    private Selector selector = null;
    private SelectionKey[] serverSelectionKeys = null;
    private ByteBuffer[] buffers = null;
    private Statistic statistic = null;
    private long statisticWindowEnd;

    private List<String> mcAddresses = null;

    @Override
    public void run() {
	super.run();

	while (true) {
	    AbstractRequest request;

	    try {
		request = queue.take();
		request.setDequeueTime(System.currentTimeMillis());
		LOG.debug("Q>W  {}", request.toString());
	    } catch (InterruptedException e) {
		LOG.warn("Exception occured while taking request from queue: {}", e);
		continue;
	    }

	    // get messages from request
	    ServerMessage[] msgs = request.getServerMessages();

	    // send messages to servers
	    for (ServerMessage msg : msgs) {
		buffers[0].clear();
		buffers[0].put(msg.getContent());
		buffers[0].flip();

		int serverId = msg.getServerId();
		SocketChannel serverSocketChannel = (SocketChannel) serverSelectionKeys[serverId]
			.channel();

		try {
		    while (buffers[0].hasRemaining()) {
			serverSocketChannel.write(buffers[0]);
		    }
		    request.setServerStartTime(serverId, System.currentTimeMillis());
		    LOG.debug("W>S{}  {}", serverId, msg.toString());
		} catch (IOException e) {
		    LOG.error("Error writing message to server: {}", e);
		}
	    }

	    // reset all buffers
	    for (int i = 0; i < buffers.length; i++) {
		buffers[i].clear();
	    }

	    boolean hasAllServerResponse = false;

	    // collect responses for each message
	    while (!hasAllServerResponse) {

		Set<SelectionKey> selectedKeys;
		try {
		    int updatedChannels = selector.select();

		    if (updatedChannels == 0) {
			LOG.debug("No updated channels");
			continue;
		    }

		    selectedKeys = selector.selectedKeys();

		} catch (IOException e1) {
		    LOG.error("Error selecting channels {}", e1.getMessage());
		    continue;
		}

		Iterator<SelectionKey> iterator = selectedKeys.iterator();

		while (iterator.hasNext() && !hasAllServerResponse) {
		    SelectionKey selectionKey = iterator.next();
		    iterator.remove();

		    long serverEndTime = System.currentTimeMillis();

		    if (!selectionKey.isValid()) {
			throw new RuntimeException("Invalid Selection Key -> Wanted to check if this can happen");
		    }

		    if (selectionKey.isReadable()) {
			SocketChannel serverSocketChannel = (SocketChannel) selectionKey.channel();
			Integer serverId = (Integer) selectionKey.attachment();

			try {
			    int byteCount = serverSocketChannel.read(buffers[serverId]);

			    if (byteCount < 1) {
				LOG.warn("number of bytes read: {} (-1 stands for end of stream)", byteCount);
				continue;
			    }

			    if (LOG.isDebugEnabled()) {
				LOG.debug("W<S{}  {}", serverId, DecoderUtil.decode(buffers[serverId]));
			    }
			    request.setServerEndTime(serverId, serverEndTime);
			    hasAllServerResponse = request.putServerResponse(serverId, buffers[serverId]);

			} catch (IOException e) {
			    LOG.error("Error reading server socket channel: {}", e);
			}
		    }
		}
	    }

	    ByteBuffer clientResponseBuffer = request.getClientResponseBuffer();

	    if (clientResponseBuffer != null) {
		clientResponseBuffer.flip();
		SocketChannel clientSocketChannel = request.getClientSocketChannel();
		try {
		    while (clientResponseBuffer.hasRemaining()) {
			clientSocketChannel.write(clientResponseBuffer);
		    }
		    if (LOG.isDebugEnabled()) {
			LOG.debug("C<W  {}", DecoderUtil.decode(clientResponseBuffer));
		    }
		} catch (IOException e) {
		    LOG.error("Error writing response to client: {}", e);
		}
	    }

	    long processEndTime = System.currentTimeMillis();
	    request.setProcessEndTime(processEndTime);

	    while ((statisticWindowEnd - processEndTime) < 0) { // TODO [nku] maybe change because initially makes no
								// sense
		statistic.report();
		statisticWindowEnd += STATS_WINDOWS_SIZE;
		statistic.reset();
	    }

	    statistic.update(request);

	    // TODO [nku] look at performance impact of logging stats
//	    LOG.info("{} {} {} {} {} {} {}",
//		    request.getType(),
//		    request.getProcessStartTime(),
//		    request.getEnqueueTime(),
//		    request.getDequeueTime(),
//		    request.getProcessEndTime(),
//		    request.getHitCount(),
//		    request.getKeyCount());
	}
    }

    public WorkerThread withId(int id) {
	this.id = id;
	return this;
    }

    public WorkerThread withQueue(BlockingQueue<AbstractRequest> queue) {
	this.queue = queue;
	return this;
    }

    public WorkerThread withMcAddresses(List<String> mcAddresses) {
	this.mcAddresses = mcAddresses;
	return this;
    }

    public WorkerThread withPriority(int priority) {
	setPriority(priority);
	return this;
    }

    public WorkerThread withStatistic(Statistic statistic) {
	this.statistic = statistic;
	return this;
    }

    public WorkerThread withStart(long start) {
	this.statisticWindowEnd = start + 5000;
	return this;
    }

    public WorkerThread withUncaughtExceptionHandler(UncaughtExceptionHandler uncaughtExceptionHandler) {
	setUncaughtExceptionHandler(uncaughtExceptionHandler);
	return this;
    }

    public WorkerThread create() {
	LOG.debug("Creating worker thread " + this.id + "...");

	assert (id != -1);
	assert (queue != null);
	assert (mcAddresses != null);

	try {
	    selector = Selector.open();
	    serverSelectionKeys = new SelectionKey[mcAddresses.size()];
	    buffers = new ByteBuffer[mcAddresses.size()];

	    for (int i = 0; i < mcAddresses.size(); i++) {
		String[] mcAddress = mcAddresses.get(i).split(":");
		String ip = mcAddress[0];
		int port = Integer.parseInt(mcAddress[1]);

		SocketChannel socketChannel = SocketChannel.open();
		socketChannel.connect(new InetSocketAddress(ip, port));
		socketChannel.configureBlocking(false);

		SelectionKey selectionKey = socketChannel.register(selector, SelectionKey.OP_READ, i);
		serverSelectionKeys[i] = selectionKey;

		buffers[i] = ByteBuffer.allocate(BUFFER_SIZE);
	    }

	} catch (IOException e) {
	    LOG.error("Error opening server socket channel: {}", e);
	}

	return this;
    }

}
