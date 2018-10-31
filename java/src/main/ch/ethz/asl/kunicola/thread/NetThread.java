package ch.ethz.asl.kunicola.thread;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.ClosedByInterruptException;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.Set;
import java.util.concurrent.BlockingQueue;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.util.RequestDecoder;

public class NetThread extends Thread {

	private final static Logger LOG = LogManager.getLogger();
	public final static int BUFFER_SIZE = 8192;

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
		try {
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

						long processStartTime = System.nanoTime() / 1000; // in microseconds

						if (!selectionKey.isValid()) {
							throw new RuntimeException("Invalid Selection Key -> Wanted to check if this can happen");
						}

						if (selectionKey.isAcceptable()) {
							serverSocketChannel.accept()
									.configureBlocking(false)
									.register(selector, SelectionKey.OP_READ);

							LOG.debug("C>N  accepting new client");
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
							if (byteCount < 1) {
								LOG.debug("number of bytes read: {} (-1 stands for end of stream)", byteCount);
								continue;
							}

							boolean hasMore; // multiple commands in buffer
							do {
								AbstractRequest request = requestDecoder.decode(buffer);
								hasMore = requestDecoder.hasMore();

								if (request != null) { // request complete
									selectionKey.attach(null);
									if (!request.getType().equals("unknown")) { // known request
										request.setClientSocketChannel(clientSocketChannel);

										long enqueueTime = System.nanoTime() / 1000; // in microseconds
										request.setProcessStartTime(processStartTime);
										request.setEnqueueTime(enqueueTime);

										queue.put(request);

										LOG.debug("C>N>Q {}", request);
									}

								} else { // request incomplete -> attach dedicated buffer to selection key
									selectionKey.attach(buffer);
									LOG.debug("C>N  incomplete request");
								}
							} while (hasMore);
						}
					}
				} catch (ClosedByInterruptException e) {
					throw new InterruptedException();
				} catch (IOException e) {
					LOG.error("NetThread IOException: " + e.getMessage());
				}
			}
		} catch (InterruptedException e) {
			LOG.info("NetThread Interrupted");
			Thread.currentThread().interrupt(); // restore interrupt flag
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

	public NetThread withUncaughtExceptionHandler(UncaughtExceptionHandler uncaughtExceptionHandler) {
		setUncaughtExceptionHandler(uncaughtExceptionHandler);
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

		requestDecoder = new RequestDecoder().withShardedMultiGet(readSharded)
				.withNumberOfServers(numberOfServers);

		return this;
	}

}
