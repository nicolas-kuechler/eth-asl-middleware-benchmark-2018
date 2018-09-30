package ch.ethz.asl.kunicola.thread;

import java.util.List;
import java.util.concurrent.BlockingQueue;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractClientRequest;

public class WorkerThread extends Thread {

    private final static Logger LOG = LogManager.getLogger();

    private int id = -1;
    private BlockingQueue<AbstractClientRequest> queue = null;

    private List<String> mcAddresses = null;
    private Boolean readSharded = null;

    @Override
    public void run() {
	super.run();

	// TODO [nku] implement worker thread

	while (true) {
	    try {
		AbstractClientRequest request = queue.take();

		request.process();

	    } catch (InterruptedException e) {

		e.printStackTrace();
	    }
	}
    }

    public WorkerThread withId(int id) {
	this.id = id;
	return this;
    }

    public WorkerThread withQueue(BlockingQueue<AbstractClientRequest> queue) {
	this.queue = queue;
	return this;
    }

    public WorkerThread withMcAddresses(List<String> mcAddresses) {
	this.mcAddresses = mcAddresses;
	return this;
    }

    public WorkerThread withReadSharded(boolean readSharded) {
	this.readSharded = readSharded;
	return this;
    }

    public WorkerThread create() {
	LOG.debug("Creating worker thread " + this.id + "...");

	assert (id != -1);
	assert (queue != null);
	assert (mcAddresses != null);
	assert (readSharded != null);

	// TODO [nku] build connection to servers

	return this;
    }

}
