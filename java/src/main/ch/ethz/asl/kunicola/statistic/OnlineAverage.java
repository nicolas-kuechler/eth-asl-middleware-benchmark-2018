package ch.ethz.asl.kunicola.statistic;

public class OnlineAverage {

    private long count;
    private double mean;
    private double m2;

    public void update(long newMeasurement) {
	count++;
	double delta1 = newMeasurement - mean;
	mean = mean + delta1 / count;
	double delta2 = newMeasurement - mean;
	m2 = m2 + delta1 * delta2;
    }

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
