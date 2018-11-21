package ch.ethz.asl.kunicola.statistic;

/**
 * Implements Welford's Online algorithm for calculating mean and variance
 * 
 * @author nicolas-kuechler
 *
 */
public class OnlineAverage {

	private long count;
	private double mean;
	private double m2;

	/**
	 * update the online statistics with a new measurement
	 * 
	 * @param newMeasurement
	 */
	public void update(long newMeasurement) {
		count++;
		double delta1 = newMeasurement - mean;
		mean = mean + delta1 / count;
		double delta2 = newMeasurement - mean;
		m2 = m2 + delta1 * delta2;
	}

	/**
	 * reset the online average
	 */
	public void reset() {
		count = 0;
		mean = 0.0;
		m2 = 0.0;
	}

	public long getCount() {
		return count;
	}

	public double getMean() {
		return mean;
	}

	public double getM2() {
		return m2;
	}
}
