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
import java.util.concurrent.atomic.AtomicLong;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.util.BufferTimePair;
import ch.ethz.asl.kunicola.util.DecoderUtil;
import ch.ethz.asl.kunicola.util.RequestDecoder;

/**
 * Accepts client connections, reads request into a buffer and decodes it to
 * check if the request is valid and complete. Then if the request is both valid
 * and complete it is placed into the queue.
 * 
 * @author nicolas-kuechler
 *
 */
public class NetThread extends Thread {

	private final static Logger LOG = LogManager.getLogger();
	public final static int BUFFER_SIZE = 8192;

	private BlockingQueue<AbstractRequest> queue;
	private AtomicLong arrivalCounter;

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

						long processStartTime = System.nanoTime() / 100000; // in 100 microseconds

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

							ByteBuffer buffer;
							if (hasBuffer) {
								// use time and buffer of first part of request
								BufferTimePair btPair = (BufferTimePair) obj;
								buffer = btPair.getBuffer();
								processStartTime = btPair.getTime();

							} else {
								buffer = ByteBuffer.allocate(BUFFER_SIZE);
							}
							try {

								int byteCount = clientSocketChannel.read(buffer);
								if (byteCount < 1) {
									LOG.debug("number of bytes read: {} (-1 stands for end of stream)", byteCount);
									continue;
								}
							} catch (ClosedByInterruptException e) {
								throw new InterruptedException();
							} catch (IOException e) {
								LOG.info("close client socket connection");
								clientSocketChannel.close();
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

										long enqueueTime = System.nanoTime() / 100000; // in 100 microseconds
										request.setProcessStartTime(processStartTime);
										request.setEnqueueTime(enqueueTime);

										queue.put(request);
										arrivalCounter.incrementAndGet();
										LOG.debug("C>N>Q {}", request);
									} else {
										// unknown request -> return error to client
										ByteBuffer clientResponseBuffer = ByteBuffer.allocate(512);
										clientResponseBuffer.put("ERROR\r\n".getBytes());
										clientResponseBuffer.flip();
										try {
											while (clientResponseBuffer.hasRemaining()) {
												clientSocketChannel.write(clientResponseBuffer);
											}
											if (LOG.isDebugEnabled()) {
												LOG.debug("C<N  {}", DecoderUtil.decode(clientResponseBuffer));
											}
										} catch (ClosedByInterruptException e) {
											throw new InterruptedException();
										} catch (IOException e) {
											LOG.error("Error writing response to client: {}", e);
										}

									}

								} else { // request incomplete -> attach dedicated buffer to selection key
									BufferTimePair btPair = new BufferTimePair(buffer, processStartTime);
									selectionKey.attach(btPair);
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

	public NetThread withArrivalCounter(AtomicLong arrivalCounter) {
		this.arrivalCounter = arrivalCounter;
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
