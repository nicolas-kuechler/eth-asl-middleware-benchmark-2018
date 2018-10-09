package ch.ethz.asl.kunicola.thread;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.time.Instant;
import java.util.Iterator;
import java.util.Set;
import java.util.concurrent.BlockingQueue;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.Marker;
import org.apache.logging.log4j.MarkerManager;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.request.RequestDecoder;

public class NetThread extends Thread {

    private final static Logger LOG = LogManager.getLogger();
    private final static Marker marker = MarkerManager.getMarker("NETTHREAD");
    private final static int BUFFER_SIZE = 8192;

    private BlockingQueue<AbstractRequest> queue;

    private Selector selector;
    private ServerSocketChannel serverSocketChannel;

    private RequestDecoder requestDecoder;

    private String myIp;
    private int myPort;
    private boolean readSharded;
    private int numberOfServers;

    @Override
    public void run() {
	super.run();

	while (true) {
	    try {
		int updatedChannels = selector.select();
		if (updatedChannels == 0) {
		    LOG.debug("No updated channels");
		    continue;
		}

		Set<SelectionKey> selectedKeys = selector.selectedKeys();
		Iterator<SelectionKey> iterator = selectedKeys.iterator();

		while (iterator.hasNext()) {
		    SelectionKey selectionKey = iterator.next();
		    iterator.remove();

		    Instant processStartTime = Instant.now();

		    if (!selectionKey.isValid()) {
			throw new RuntimeException("Invalid Selection Key -> Wanted to check if this can happen");
		    }

		    if (selectionKey.isAcceptable()) {
			serverSocketChannel.accept()
				.configureBlocking(false)
				.register(selector, SelectionKey.OP_READ);

			LOG.debug(marker, "C>N  accepting new client");
		    }

		    if (selectionKey.isReadable()) {
			SocketChannel clientSocketChannel = (SocketChannel) selectionKey.channel();

			Object obj = selectionKey.attachment();
			boolean hasBuffer = obj != null;

			ByteBuffer buffer; // TODO [nku] improve by reusing one buffer
			if (hasBuffer) {
			    buffer = (ByteBuffer) obj;
			} else {
			    buffer = ByteBuffer.allocate(BUFFER_SIZE);
			}

			int byteCount = clientSocketChannel.read(buffer);
			if (byteCount < 1) { // TODO [nku] check if this needs special handling
			    continue;
			}

			AbstractRequest request = requestDecoder.decode(buffer);

			if (request != null) { // request complete
			    request.setClientSocketChannel(clientSocketChannel);
			    selectionKey.attach(null);

			    Instant enqueueTime = Instant.now();
			    request.setProcessStartTime(processStartTime);
			    request.setEnqueueTime(enqueueTime);

			    queue.put(request);

			    LOG.debug(marker, "C>N>Q {}", request.toString());

			} else { // request incomplete -> attach dedicated buffer to selection key
			    selectionKey.attach(buffer);
			    LOG.debug(marker, "C>N  incomplete request");
			}
		    }
		}
	    } catch (IOException | InterruptedException e) {
		LOG.error("IOException: " + e.getMessage());
	    }
	}
    }

    public NetThread withQueue(BlockingQueue<AbstractRequest> queue) {
	this.queue = queue;
	return this;
    }

    public NetThread withIp(String myIp) {
	this.myIp = myIp;
	return this;
    }

    public NetThread withPort(int myPort) {
	this.myPort = myPort;
	return this;
    }

    public NetThread withReadSharded(boolean readSharded) {
	this.readSharded = readSharded;
	return this;
    }

    public NetThread withNumberOfServers(int numberOfServers) {
	this.numberOfServers = numberOfServers;
	return this;
    }

    public NetThread withPriority(int priority) {
	setPriority(priority);
	return this;
    }

    public NetThread create() throws IOException {
	LOG.debug(marker, "Creating net thread...");

	assert (myIp != null);
	assert (myPort != 0);

	selector = Selector.open();
	serverSocketChannel = ServerSocketChannel.open();

	serverSocketChannel.bind(new InetSocketAddress(myIp, myPort))
		.configureBlocking(false)
		.register(selector, SelectionKey.OP_ACCEPT);

	requestDecoder = new RequestDecoder().withShardedMultiGet(readSharded).withNumberOfServers(numberOfServers);

	return this;
    }

}
