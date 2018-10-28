package ch.ethz.asl.kunicola.statistic;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractRequest;

//TODO [nku] add junit test
public class Statistic {

    public final static String HEADER = "time tid slot type "
	    + "qwt_count qwt_mean qwt_m2 "
	    + "rt_count rt_mean rt_m2 "
	    + "ntt_count ntt_mean ntt_m2 "
	    + "wtt_count wtt_mean wtt_m2";

    private final static Logger STATS_LOG = LogManager.getLogger("stat");

    OnlineAverage queueWaitingTime;

    OnlineAverage getResponseTime;
    OnlineAverage setResponseTime;
    OnlineAverage multiGetResponseTime;

    OnlineAverage[] getServerServiceTime;
    OnlineAverage[] setServerServiceTime;
    OnlineAverage[] multiGetServerServiceTime;

    OnlineAverage getNetThreadTime;
    OnlineAverage setNetThreadTime;
    OnlineAverage multiGetNetThreadTime;

    OnlineAverage getWorkerThreadTime;
    OnlineAverage setWorkerThreadTime;
    OnlineAverage multiGetWorkerThreadTime;

    private int numberOfServers;

    private int windowsSlot;

    public Statistic(int numberofServers) {
	this.numberOfServers = numberofServers;
	this.windowsSlot = 0;

	queueWaitingTime = new OnlineAverage();
	queueWaitingTime = new OnlineAverage();

	getResponseTime = new OnlineAverage();
	setResponseTime = new OnlineAverage();
	multiGetResponseTime = new OnlineAverage();

	getServerServiceTime = new OnlineAverage[numberofServers];
	setServerServiceTime = new OnlineAverage[numberofServers];
	multiGetServerServiceTime = new OnlineAverage[numberofServers];

	for (int i = 0; i < numberofServers; i++) {
	    getServerServiceTime[i] = new OnlineAverage();
	    setServerServiceTime[i] = new OnlineAverage();
	    multiGetServerServiceTime[i] = new OnlineAverage();
	}

	getNetThreadTime = new OnlineAverage();
	setNetThreadTime = new OnlineAverage();
	multiGetNetThreadTime = new OnlineAverage();

	getWorkerThreadTime = new OnlineAverage();
	setWorkerThreadTime = new OnlineAverage();
	multiGetWorkerThreadTime = new OnlineAverage();
    }

    public void update(AbstractRequest request) {
	queueWaitingTime.update(request.getDequeueTime() - request.getEnqueueTime());
	String type = request.getType();

	if (type.equals("get")) {

	    getResponseTime.update(request.getProcessEndTime() - request.getProcessStartTime());

	    for (int serverId = 0; serverId < getServerServiceTime.length; serverId++) {
		Long serverEndTime = request.getServerEndTime()[serverId];
		Long serverStartTime = request.getServerStartTime()[serverId];
		if (serverEndTime != null && serverStartTime != null) {
		    getServerServiceTime[serverId].update(serverEndTime - serverStartTime);
		}
	    }

	    getNetThreadTime.update(request.getEnqueueTime() - request.getProcessStartTime());
	    getWorkerThreadTime.update(request.getProcessEndTime() - request.getDequeueTime());

	} else if (type.equals("set")) {
	    setResponseTime.update(request.getProcessEndTime() - request.getProcessStartTime());

	    for (int serverId = 0; serverId < setServerServiceTime.length; serverId++) {
		Long serverEndTime = request.getServerEndTime()[serverId];
		Long serverStartTime = request.getServerStartTime()[serverId];
		if (serverEndTime != null && serverStartTime != null) {
		    setServerServiceTime[serverId].update(serverEndTime - serverStartTime);
		}
	    }

	    setNetThreadTime.update(request.getEnqueueTime() - request.getProcessStartTime());
	    setWorkerThreadTime.update(request.getProcessEndTime() - request.getDequeueTime());

	} else if (type.equals("multi-get")) {
	    multiGetResponseTime.update(request.getProcessEndTime() - request.getProcessStartTime());

	    for (int serverId = 0; serverId < multiGetServerServiceTime.length; serverId++) {
		Long serverEndTime = request.getServerEndTime()[serverId];
		Long serverStartTime = request.getServerStartTime()[serverId];
		if (serverEndTime != null && serverStartTime != null) {
		    multiGetServerServiceTime[serverId].update(serverEndTime - serverStartTime);
		}
	    }

	    multiGetNetThreadTime.update(request.getEnqueueTime() - request.getProcessStartTime());
	    multiGetWorkerThreadTime.update(request.getProcessEndTime() - request.getDequeueTime());
	} else {
	    throw new IllegalArgumentException("Unrecognized Request Type: " + type);
	}

    }

    public void reset() {
	queueWaitingTime.reset();

	getResponseTime.reset();
	setResponseTime.reset();
	multiGetResponseTime.reset();

	for (int i = 0; i < numberOfServers; i++) {
	    getServerServiceTime[i].reset();
	    setServerServiceTime[i].reset();
	    multiGetServerServiceTime[i].reset();
	}

	getNetThreadTime.reset();
	setNetThreadTime.reset();
	multiGetNetThreadTime.reset();

	getWorkerThreadTime.reset();
	setWorkerThreadTime.reset();
	multiGetWorkerThreadTime.reset();

	windowsSlot += 1;
    }

    public void report() {
	STATS_LOG.info("{} get {} {} {} {} {} {} {} {} {} {} {} {}",
		windowsSlot,
		queueWaitingTime.getCount(), queueWaitingTime.getMean(), queueWaitingTime.getM2(),
		getResponseTime.getCount(), getResponseTime.getMean(), getResponseTime.getM2(),
		getNetThreadTime.getCount(), getNetThreadTime.getMean(), getNetThreadTime.getM2(),
		getWorkerThreadTime.getCount(), getWorkerThreadTime.getMean(), getWorkerThreadTime.getM2());

	STATS_LOG.info("{} set {} {} {} {} {} {} {} {} {} {} {} {}",
		windowsSlot,
		queueWaitingTime.getCount(), queueWaitingTime.getMean(), queueWaitingTime.getM2(),
		setResponseTime.getCount(), setResponseTime.getMean(), setResponseTime.getM2(),
		setNetThreadTime.getCount(), setNetThreadTime.getMean(), setNetThreadTime.getM2(),
		setWorkerThreadTime.getCount(), setWorkerThreadTime.getMean(), setWorkerThreadTime.getM2());

	STATS_LOG.info("{} mget {} {} {} {} {} {} {} {} {} {} {} {}",
		windowsSlot,
		queueWaitingTime.getCount(), queueWaitingTime.getMean(), queueWaitingTime.getM2(),
		multiGetResponseTime.getCount(), multiGetResponseTime.getMean(), multiGetResponseTime.getM2(),
		multiGetNetThreadTime.getCount(), multiGetNetThreadTime.getMean(), multiGetNetThreadTime.getM2(),
		multiGetWorkerThreadTime.getCount(), multiGetWorkerThreadTime.getMean(),
		multiGetWorkerThreadTime.getM2());
    }

}
