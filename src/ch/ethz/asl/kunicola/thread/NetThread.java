package ch.ethz.asl.kunicola.thread;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.util.Iterator;
import java.util.Set;
import java.util.concurrent.BlockingQueue;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.BufferPool;
import ch.ethz.asl.kunicola.request.AbstractClientRequest;
import ch.ethz.asl.kunicola.request.SetClientRequest;

public class NetThread extends Thread {

    private final static Logger LOG = LogManager.getLogger();
    private static final Charset charset = Charset.forName("UTF-8");

    private BlockingQueue<AbstractClientRequest> queue;

    private Selector selector;
    private ServerSocketChannel serverSocketChannel;

    private String myIp;
    private int myPort;

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

		    if (!selectionKey.isValid()) {
			throw new RuntimeException("Invalid Selection Key -> Wanted to check if this can happen");
		    }

		    if (selectionKey.isAcceptable()) {
			serverSocketChannel.accept()
				.configureBlocking(false)
				.register(selector, SelectionKey.OP_READ);

			LOG.debug("Accepted new Client: " + selectionKey.hashCode());
		    }

		    if (selectionKey.isReadable()) {
			SocketChannel clientSocketChannel = (SocketChannel) selectionKey.channel();

			Object obj = selectionKey.attachment(); // if key has no buffer attached get one from the pool
			ByteBuffer buffer = (obj == null) ? BufferPool.getBuffer() : (ByteBuffer) obj;

			int byteCount = clientSocketChannel.read(buffer);
			if (byteCount < 1) { // TODO [nku] check if this needs special handling
			    continue;
			}

			// TODO [nku] check if memtier clients sometimes send
			// more than a single message and thus don't end with \r\n
			int pos = buffer.position();
			if (buffer.get(pos - 2) == '\r'
				&& buffer.get(pos - 1) == '\n') {
			    buffer.flip();
			    String requestString = charset.decode(buffer).toString();

			    LOG.debug("Request String: " + requestString);

			    // TODO [nku] build request
			    AbstractClientRequest request = new SetClientRequest()
				    .with(clientSocketChannel)
				    .withRequestString(requestString);
			    queue.put(request);

			    // return buffer to pool
			    selectionKey.attach(null);
			    BufferPool.putBuffer(buffer);
			} else { // incomplete request
			    LOG.info("Incomplete Request");
			    // attach buffer to key to continue next time
			    selectionKey.attach(buffer);
			}
		    }
		}
	    } catch (IOException | InterruptedException e) {
		LOG.error("IOException: " + e.getMessage());
	    }
	}
    }

    public NetThread withQueue(BlockingQueue<AbstractClientRequest> queue) {
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

    public NetThread create() throws IOException {
	LOG.debug("Creating net thread...");

	assert (myIp != null);
	assert (myPort != 0);

	selector = Selector.open();
	serverSocketChannel = ServerSocketChannel.open();

	serverSocketChannel.bind(new InetSocketAddress(myIp, myPort))
		.configureBlocking(false)
		.register(selector, SelectionKey.OP_ACCEPT);

	return this;
    }

}
