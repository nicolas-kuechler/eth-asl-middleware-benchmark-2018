package ch.ethz.asl.kunicola.statistic;

import java.util.HashMap;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import ch.ethz.asl.kunicola.request.AbstractRequest;

/**
 * Handles all request related statistics updates, reports and resets.
 * 
 * @author nicolas-kuechler
 *
 */
public class Statistic {

	private final static Logger STATS_LOG = LogManager.getLogger("stat");
	private final static int HIST_HASHMAP_SIZE = 500;

	private final int numberOfServers;
	private int slot; // enumerates all the 5 second windows

	private long totalHitCount = 0; // total number of cache hits
	private long totalKeyCount = 0; // total number of keys (get/mget) in the forwarded requests

	private long totalGetCount = 0;
	private long totalMGetCount = 0;
	private long totalSetCount = 0;

	private OnlineAverage queueWaitingTime;

	private OnlineAverage getResponseTime;
	private OnlineAverage setResponseTime;
	private OnlineAverage mgetResponseTime;

	private OnlineAverage[] getServerServiceTime;
	private OnlineAverage getTotalServerServiceTime;

	private OnlineAverage[] setServerServiceTime;
	private OnlineAverage setTotalServerServiceTime;

	private OnlineAverage[] mgetServerServiceTime;
	private OnlineAverage mgetTotalServerServiceTime;

	private OnlineAverage getNetThreadTime;
	private OnlineAverage setNetThreadTime;
	private OnlineAverage mgetNetThreadTime;

	private OnlineAverage getWorkerThreadTime;
	private OnlineAverage setWorkerThreadTime;
	private OnlineAverage mgetWorkerThreadTime;

	private HashMap<Long, Integer> getResponseTimeHist = new HashMap<>(HIST_HASHMAP_SIZE);
	private HashMap<Long, Integer> setResponseTimeHist = new HashMap<>(HIST_HASHMAP_SIZE);
	private HashMap<Long, Integer> mgetResponseTimeHist = new HashMap<>(HIST_HASHMAP_SIZE);

	public Statistic(int numberofServers) {
		this.numberOfServers = numberofServers;
		this.slot = 0;

		queueWaitingTime = new OnlineAverage();
		queueWaitingTime = new OnlineAverage();

		getResponseTime = new OnlineAverage();
		setResponseTime = new OnlineAverage();
		mgetResponseTime = new OnlineAverage();

		getTotalServerServiceTime = new OnlineAverage();
		setTotalServerServiceTime = new OnlineAverage();
		mgetTotalServerServiceTime = new OnlineAverage();

		getServerServiceTime = new OnlineAverage[numberofServers];
		setServerServiceTime = new OnlineAverage[numberofServers];
		mgetServerServiceTime = new OnlineAverage[numberofServers];

		for (int i = 0; i < numberofServers; i++) {
			getServerServiceTime[i] = new OnlineAverage();
			setServerServiceTime[i] = new OnlineAverage();
			mgetServerServiceTime[i] = new OnlineAverage();
		}

		getNetThreadTime = new OnlineAverage();
		setNetThreadTime = new OnlineAverage();
		mgetNetThreadTime = new OnlineAverage();

		getWorkerThreadTime = new OnlineAverage();
		setWorkerThreadTime = new OnlineAverage();
		mgetWorkerThreadTime = new OnlineAverage();

	}

	/**
	 * Update all statistics with the measurements from the request
	 * 
	 * @param request
	 */
	public void update(AbstractRequest request) {
		totalHitCount += request.getHitCount();
		totalKeyCount += request.getKeyCount();

		long queueWaitingTimeMeasurement = (request.getDequeueTime() - request.getEnqueueTime());

		long responseTime = (request.getProcessEndTime() - request.getProcessStartTime());
		long netThreadTime = (request.getEnqueueTime() - request.getProcessStartTime());
		long workerThreadTime = (request.getProcessEndTime() - request.getDequeueTime());

		queueWaitingTime.update(queueWaitingTimeMeasurement);
		String type = request.getType();

		if (type.equals("get")) {
			totalGetCount++;
			getResponseTime.update(responseTime);
			getResponseTimeHist.merge(responseTime, 1, Integer::sum);

			Long minServerStartTime = null;
			Long maxServerEndTime = null;

			for (int serverId = 0; serverId < getServerServiceTime.length; serverId++) {
				Long serverEndTime = request.getServerEndTime()[serverId];
				Long serverStartTime = request.getServerStartTime()[serverId];
				if (serverEndTime != null && serverStartTime != null) {
					long serverServiceTime = (serverEndTime - serverStartTime);
					getServerServiceTime[serverId].update(serverServiceTime);

					if (serverStartTime > 0 && (minServerStartTime == null || minServerStartTime > serverStartTime)) {
						minServerStartTime = serverStartTime;
					}
					if (maxServerEndTime == null || maxServerEndTime < serverEndTime) {
						maxServerEndTime = serverEndTime;
					}
				}
			}

			if (maxServerEndTime != null && minServerStartTime != null) {
				long totalServerServiceTime = (maxServerEndTime - minServerStartTime);
				getTotalServerServiceTime.update(totalServerServiceTime);
			}

			getNetThreadTime.update(netThreadTime);
			getWorkerThreadTime.update(workerThreadTime);

		} else if (type.equals("set")) {
			totalSetCount++;
			setResponseTime.update(responseTime);
			setResponseTimeHist.merge(responseTime, 1, Integer::sum);

			Long minServerStartTime = null;
			Long maxServerEndTime = null;

			for (int serverId = 0; serverId < setServerServiceTime.length; serverId++) {
				Long serverEndTime = request.getServerEndTime()[serverId];
				Long serverStartTime = request.getServerStartTime()[serverId];
				if (serverEndTime != null && serverStartTime != null) {
					long serverServiceTime = (serverEndTime - serverStartTime);
					setServerServiceTime[serverId].update(serverServiceTime);

					if (serverStartTime > 0 && (minServerStartTime == null || minServerStartTime > serverStartTime)) {
						minServerStartTime = serverStartTime;
					}
					if (maxServerEndTime == null || maxServerEndTime < serverEndTime) {
						maxServerEndTime = serverEndTime;
					}
				}
			}
			if (maxServerEndTime != null && minServerStartTime != null) {
				long totalServerServiceTime = (maxServerEndTime - minServerStartTime);
				setTotalServerServiceTime.update(totalServerServiceTime);
			}

			setNetThreadTime.update(netThreadTime);
			setWorkerThreadTime.update(workerThreadTime);

		} else if (type.equals("mget")) {
			totalMGetCount++;

			mgetResponseTime.update(responseTime);
			mgetResponseTimeHist.merge(responseTime, 1, Integer::sum);

			Long minServerStartTime = null;
			Long maxServerEndTime = null;

			for (int serverId = 0; serverId < mgetServerServiceTime.length; serverId++) {
				Long serverEndTime = request.getServerEndTime()[serverId];
				Long serverStartTime = request.getServerStartTime()[serverId];
				if (serverEndTime != null && serverStartTime != null) {
					long serverServiceTime = (serverEndTime - serverStartTime);
					mgetServerServiceTime[serverId].update(serverServiceTime);

					if (serverStartTime > 0 && (minServerStartTime == null || minServerStartTime > serverStartTime)) {
						minServerStartTime = serverStartTime;
					}
					if (maxServerEndTime == null || maxServerEndTime < serverEndTime) {
						maxServerEndTime = serverEndTime;
					}
				}
			}

			if (maxServerEndTime != null && minServerStartTime != null) {
				long totalServerServiceTime = (maxServerEndTime - minServerStartTime);
				mgetTotalServerServiceTime.update(totalServerServiceTime);
			}

			mgetNetThreadTime.update(netThreadTime);
			mgetWorkerThreadTime.update(workerThreadTime);
		} else {
			throw new IllegalArgumentException("Unrecognized Request Type: " + type);
		}

	}

	/**
	 * reset all collected statistics (usually done every 5 seconds after statistics
	 * were logged)
	 */
	public void reset() {
		queueWaitingTime.reset();

		getResponseTime.reset();
		setResponseTime.reset();
		mgetResponseTime.reset();

		getTotalServerServiceTime.reset();
		setTotalServerServiceTime.reset();
		mgetTotalServerServiceTime.reset();

		for (int i = 0; i < numberOfServers; i++) {
			getServerServiceTime[i].reset();
			setServerServiceTime[i].reset();
			mgetServerServiceTime[i].reset();
		}

		getNetThreadTime.reset();
		setNetThreadTime.reset();
		mgetNetThreadTime.reset();

		getWorkerThreadTime.reset();
		setWorkerThreadTime.reset();
		mgetWorkerThreadTime.reset();

		setResponseTimeHist.clear();
		getResponseTimeHist.clear();
		mgetResponseTimeHist.clear();

		slot += 1;
	}

	/**
	 * write collected statistics to file
	 */
	public void report() {

		StringBuilder getBuilder = new StringBuilder();
		StringBuilder setBuilder = new StringBuilder();
		StringBuilder mgetBuilder = new StringBuilder();

		for (int i = 0; i < numberOfServers; i++) {
			getBuilder.append(getServerServiceTime[i].getCount());
			getBuilder.append("; ");
			getBuilder.append(getServerServiceTime[i].getMean());
			getBuilder.append("; ");
			getBuilder.append(getServerServiceTime[i].getM2());
			getBuilder.append("; ");

			setBuilder.append(setServerServiceTime[i].getCount());
			setBuilder.append("; ");
			setBuilder.append(setServerServiceTime[i].getMean());
			setBuilder.append("; ");
			setBuilder.append(setServerServiceTime[i].getM2());
			setBuilder.append("; ");

			mgetBuilder.append(mgetServerServiceTime[i].getCount());
			mgetBuilder.append("; ");
			mgetBuilder.append(mgetServerServiceTime[i].getMean());
			mgetBuilder.append("; ");
			mgetBuilder.append(mgetServerServiceTime[i].getM2());
			mgetBuilder.append("; ");

		}

		// delete last delimiter
		getBuilder.deleteCharAt(getBuilder.length() - 2);
		setBuilder.deleteCharAt(setBuilder.length() - 2);
		mgetBuilder.deleteCharAt(mgetBuilder.length() - 2);

		if (getResponseTime.getCount() > 0) {
			STATS_LOG.info("op; {}; get; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}",
					slot,
					queueWaitingTime.getCount(), queueWaitingTime.getMean(), queueWaitingTime.getM2(),
					getResponseTime.getCount(), getResponseTime.getMean(), getResponseTime.getM2(),
					getNetThreadTime.getCount(), getNetThreadTime.getMean(), getNetThreadTime.getM2(),
					getWorkerThreadTime.getCount(), getWorkerThreadTime.getMean(), getWorkerThreadTime.getM2(),
					getTotalServerServiceTime.getCount(), getTotalServerServiceTime.getMean(),
					getTotalServerServiceTime.getM2(),
					getBuilder);

			STATS_LOG.info("rt_hist; {}; get; {}", slot, getResponseTimeHist);
		}

		if (setResponseTime.getCount() > 0) {
			STATS_LOG.info("op; {}; set; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}",
					slot,
					queueWaitingTime.getCount(), queueWaitingTime.getMean(), queueWaitingTime.getM2(),
					setResponseTime.getCount(), setResponseTime.getMean(), setResponseTime.getM2(),
					setNetThreadTime.getCount(), setNetThreadTime.getMean(), setNetThreadTime.getM2(),
					setWorkerThreadTime.getCount(), setWorkerThreadTime.getMean(), setWorkerThreadTime.getM2(),
					setTotalServerServiceTime.getCount(), setTotalServerServiceTime.getMean(),
					setTotalServerServiceTime.getM2(),
					setBuilder);
			STATS_LOG.info("rt_hist; {}; set; {}", slot, setResponseTimeHist);
		}

		if (mgetResponseTime.getCount() > 0) {
			STATS_LOG.info("op; {}; mget; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}",
					slot,
					queueWaitingTime.getCount(), queueWaitingTime.getMean(), queueWaitingTime.getM2(),
					mgetResponseTime.getCount(), mgetResponseTime.getMean(), mgetResponseTime.getM2(),
					mgetNetThreadTime.getCount(), mgetNetThreadTime.getMean(), mgetNetThreadTime.getM2(),
					mgetWorkerThreadTime.getCount(), mgetWorkerThreadTime.getMean(),
					mgetWorkerThreadTime.getM2(),
					mgetTotalServerServiceTime.getCount(), mgetTotalServerServiceTime.getMean(),
					mgetTotalServerServiceTime.getM2(),
					mgetBuilder);
			STATS_LOG.info("rt_hist; {}; mget; {}", slot, mgetResponseTimeHist);
		}
	}

	/**
	 * reports a summary of the activity (cache miss ratio, request count per type,
	 * ...) of this worker (usually written when worker is stopped)
	 */
	public void reportWorkerSummary() {
		double cacheMissRatio = totalKeyCount > 0
				? 1.0 - (double) totalHitCount / totalKeyCount
				: 0.0;

		double avgNumberOfKeys = (totalGetCount + totalMGetCount) > 0
				? totalKeyCount / (double) (totalGetCount + totalMGetCount)
				: 0.0;

		STATS_LOG.info("summary; {}; {}; {}; {}; {}; {}; {}",
				totalGetCount, totalSetCount, totalMGetCount,
				totalHitCount, totalKeyCount, cacheMissRatio, avgNumberOfKeys);
	}

	/**
	 * Log file starts with a header per stat type indicating the meaning of each
	 * logged information
	 * 
	 * @param numberOfServers
	 */
	public static void reportHeaders(int numberOfServers) {

		// for stat type queue
		String queueHeader = "time; tid; stat_type; slot; size";
		STATS_LOG.info("queue; " + queueHeader);

		// for stat type arrival
		String arrivalHeader = "time; tid; stat_type; slot; arrival_count";
		STATS_LOG.info("arrival; " + arrivalHeader);

		// for stat type op
		String opHeader = getOpHeader(numberOfServers);
		STATS_LOG.info("op; " + opHeader);

		// for stat type hist
		String histHeader = "time; tid; stat_type; slot; op_type; hist";
		STATS_LOG.info("rt_hist; " + histHeader);

		// for stat type summary
		String summaryHeader = "time; tid; stat_type; total_get_count; total_set_count; total_mget_count; total_value_hit_count; total_value_count; cache_miss_ratio; avg_number_of_values";
		STATS_LOG.info("summary; " + summaryHeader);

		STATS_LOG.info("===");
	}

	private static String getOpHeader(int numberOfServers) {

		String header = "time; tid; stat_type; slot; op_type; "
				+ "qwt_count; qwt_mean; qwt_m2; "
				+ "rt_count; rt_mean; rt_m2; "
				+ "ntt_count; ntt_mean; ntt_m2; "
				+ "wtt_count; wtt_mean; wtt_m2; "
				+ "tstt_count; tstt_mean; tstt_m2";

		for (int i = 0; i < numberOfServers; i++) {
			header += String.format("; sst%d_count; sst%d_mean; sst%d_m2", i, i, i);
		}

		return header;

	}

}
