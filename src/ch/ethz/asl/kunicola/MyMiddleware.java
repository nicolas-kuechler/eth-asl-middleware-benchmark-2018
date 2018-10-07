package ch.ethz.asl.kunicola;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.thread.NetThread;
import ch.ethz.asl.kunicola.thread.WorkerThread;

public class MyMiddleware {

    final static Logger LOG = LogManager.getLogger();

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

	LOG.info("Initializing NetThread... ");
	NetThread netThread = new NetThread()
		.withIp(myIp)
		.withPort(myPort)
		.withReadSharded(readSharded)
		.withNumberOfServers(mcAddresses.size())
		.withQueue(queue)
		.create();

	netThread.start();
	LOG.info("NetThread Started with config: {}", netThread.toString());

	LOG.info("Initializing {} WorkerThreads... ", numThreadsPTP);
	for (int i = 0; i < numThreadsPTP; i++) {
	    WorkerThread workerThread = new WorkerThread()
		    .withId(i)
		    .withQueue(queue)
		    .withMcAddresses(mcAddresses)
		    .create();

	    workerThread.start();
	    LOG.info("WorkerThread {} started ", i);
	}
	LOG.info("{} WorkerThreads started with config", numThreadsPTP);

    }

    @Override
    public String toString() {
	return "MyMiddleware [myIp=" + myIp + ", myPort=" + myPort + ", mcAddresses=" + mcAddresses + ", numThreadsPTP="
		+ numThreadsPTP + ", readSharded=" + readSharded + "]";
    }

}
