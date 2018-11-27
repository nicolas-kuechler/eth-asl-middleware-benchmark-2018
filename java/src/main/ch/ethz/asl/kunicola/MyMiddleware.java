package ch.ethz.asl.kunicola;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.statistic.Statistic;
import ch.ethz.asl.kunicola.thread.NetThread;
import ch.ethz.asl.kunicola.thread.WorkerThread;
import ch.ethz.asl.kunicola.util.MiddlewareExceptionHandler;

/**
 * The application implements a middleware for memcached supporting the
 * following operations: set, get and multi-get with up to 10 keys and values of
 * 4096B.
 * 
 * When running the middleware a net-thread accepting client connections and the
 * configured number of worker threads are started. In addition the middleware
 * is collecting statistics about the queue length and number of requests over 5
 * second windows (slots). Finally a shutdow hook is registered to ensure that
 * everything is properly logged and shutdown before stopping the application.
 * 
 * @author nicolas-kuechler
 */
public class MyMiddleware {

	final static Logger LOG = LogManager.getLogger();
	final static Logger STATS_LOG = LogManager.getLogger("stat");

	final BlockingQueue<AbstractRequest> queue = new LinkedBlockingQueue<>();
	final AtomicLong arrivalCounter = new AtomicLong(0);

	private final String myIp;
	private final int myPort;
	private final List<String> mcAddresses;
	private final int numThreadsPTP;
	private final boolean readSharded;

	public MyMiddleware(String myIp, int myPort, List<String> mcAddresses, int numThreadsPTP, boolean readSharded) {
		super();
		this.myIp = myIp;
		this.myPort = myPort;
		this.mcAddresses = mcAddresses;
		this.numThreadsPTP = numThreadsPTP;
		this.readSharded = readSharded;
	}

	public void run() throws IOException {

		System.getProperties().setProperty("log4j2.contextSelector",
				"org.apache.logging.log4j.core.async.AsyncLoggerContextSelector");

		LOG.info("Middleware Started: " + this);

		Statistic.reportHeaders(mcAddresses.size());

		LOG.info("Initializing NetThread... ");
		NetThread netThread = new NetThread()
				.withIp(myIp)
				.withPort(myPort)
				.withReadSharded(readSharded)
				.withNumberOfServers(mcAddresses.size())
				.withQueue(queue)
				.withArrivalCounter(arrivalCounter)
				.withPriority(Thread.MAX_PRIORITY)
				.withUncaughtExceptionHandler(new MiddlewareExceptionHandler())
				.create();
		netThread.start();
		LOG.info("NetThread Started with config: {}", netThread.toString());

		LOG.info("Initializing {} WorkerThreads... ", numThreadsPTP);

		long start = System.nanoTime() / 100000; // in 100 microseconds
		WorkerThread[] workerThreads = new WorkerThread[numThreadsPTP];
		for (int i = 0; i < numThreadsPTP; i++) {
			workerThreads[i] = new WorkerThread()
					.withId(i)
					.withQueue(queue)
					.withMcAddresses(mcAddresses)
					.withPriority(Thread.NORM_PRIORITY)
					.withStatistic(new Statistic(mcAddresses.size()))
					.withStart(start)
					.withUncaughtExceptionHandler(new MiddlewareExceptionHandler())
					.create();

			workerThreads[i].start();
			LOG.info("WorkerThread {} started ", i);
		}
		LOG.info("{} WorkerThreads started with config", numThreadsPTP);

		ScheduledExecutorService scheduledExecutorService = Executors.newSingleThreadScheduledExecutor();

		ThreadLocal<Integer> windowSlot = new ThreadLocal<>(); // enumerate all the the logging slots
		scheduledExecutorService.scheduleWithFixedDelay(
				() -> {
					Integer slot = windowSlot.get() != null ? windowSlot.get() : 0;
					STATS_LOG.info("queue; {}; {}", slot, queue.size());
					long slotArrivalCount = arrivalCounter.getAndSet(0);
					STATS_LOG.info("arrival; {}; {}", slot, slotArrivalCount);
					slot++;
					windowSlot.set(slot);
				}, 0, 5, TimeUnit.SECONDS);

		Runtime.getRuntime().addShutdownHook(new Thread() {
			@Override
			public void run() {
				super.run();
				LOG.info("Shutdown Hook Caught Kill");

				// interrupt the NetThread
				netThread.interrupt();

				// interrupt all workers
				for (int i = 0; i < workerThreads.length; i++) {
					workerThreads[i].interrupt();
				}

				try {
					// wait for net thread to finish
					netThread.join();

					// wait for all workers to finish
					for (int i = 0; i < workerThreads.length; i++) {
						workerThreads[i].join();
					}
				} catch (InterruptedException e) {
					LOG.error("Middleware Thread got Interrupted: " + e.getMessage());
				}

				LogManager.shutdown();
			}
		});

	}

	@Override
	public String toString() {
		return "MyMiddleware [myIp=" + myIp + ", myPort=" + myPort + ", mcAddresses=" + mcAddresses + ", numThreadsPTP="
				+ numThreadsPTP + ", readSharded=" + readSharded + "]";
	}

}
