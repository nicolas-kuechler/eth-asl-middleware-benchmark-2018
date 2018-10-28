package ch.ethz.asl.kunicola;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.statistic.Statistic;
import ch.ethz.asl.kunicola.thread.NetThread;
import ch.ethz.asl.kunicola.thread.WorkerThread;
import ch.ethz.asl.kunicola.util.MiddlewareExceptionHandler;

public class MyMiddleware {

    final static Logger LOG = LogManager.getLogger();
    final static Logger STATS_LOG = LogManager.getLogger("stat");

    final BlockingQueue<AbstractRequest> queue = new LinkedBlockingQueue<>();

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
	LOG.info("Middleware Started: " + this);

	STATS_LOG.info(Statistic.HEADER);

	LOG.info("Initializing NetThread... ");
	NetThread netThread = new NetThread()
		.withIp(myIp)
		.withPort(myPort)
		.withReadSharded(readSharded)
		.withNumberOfServers(mcAddresses.size())
		.withQueue(queue)
		.withPriority(Thread.MAX_PRIORITY) // TODO [nku] see if this makes a difference
		.withUncaughtExceptionHandler(new MiddlewareExceptionHandler()) // TODO [nku] need one per thread or
										// only one for all?
		.create();
	netThread.start();
	LOG.info("NetThread Started with config: {}", netThread.toString());

	LOG.info("Initializing {} WorkerThreads... ", numThreadsPTP);

	long start = System.currentTimeMillis();

	for (int i = 0; i < numThreadsPTP; i++) {
	    WorkerThread workerThread = new WorkerThread()
		    .withId(i)
		    .withQueue(queue)
		    .withMcAddresses(mcAddresses)
		    .withPriority(Thread.NORM_PRIORITY)
		    .withStatistic(new Statistic(mcAddresses.size()))
		    .withStart(start)
		    .withUncaughtExceptionHandler(new MiddlewareExceptionHandler())
		    .create();
	    workerThread.start();
	    LOG.info("WorkerThread {} started ", i);
	}
	LOG.info("{} WorkerThreads started with config", numThreadsPTP);

	ScheduledExecutorService scheduledExecutorService = Executors.newSingleThreadScheduledExecutor();

	ThreadLocal<Integer> windowSlot = new ThreadLocal<>(); // enumerate all the the logging slots
	scheduledExecutorService.scheduleWithFixedDelay(
		() -> {
		    Integer slot = windowSlot.get() != null ? windowSlot.get() : 0;
		    STATS_LOG.info("{} queue {}", slot, queue.size());
		    slot++;
		    windowSlot.set(slot);
		}, 0, 5, TimeUnit.SECONDS);

	Runtime.getRuntime().addShutdownHook(new Thread() {
	    @Override
	    public void run() {
		super.run();
		// TODO [nku] check what else needs to be done in the cleanup
		LOG.info("Shutdown Hook Caught Kill");
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
