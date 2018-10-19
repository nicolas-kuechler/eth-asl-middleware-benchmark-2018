package ch.ethz.asl.kunicola;

import java.time.Instant;

import org.junit.Test;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.request.SetRequest;
import ch.ethz.asl.kunicola.statistic.Statistic;

public class DemoTest {

    @Test
    public void multiplicationOfZeroIntegersShouldReturnZero() {
	int numberOfServers = 2;

	Statistic statistic = new Statistic(numberOfServers);

	AbstractRequest request = new SetRequest(null, numberOfServers);

	Instant now = Instant.now();

	request.setProcessStartTime(now.toEpochMilli());
	request.setEnqueueTime(now.plusMillis(500).toEpochMilli());
	request.setDequeueTime(now.plusMillis(1000).toEpochMilli());
	request.setServerStartTime(0, now.plusMillis(1500).toEpochMilli());
	request.setServerStartTime(1, now.plusMillis(1500).toEpochMilli());
	request.setServerEndTime(0, now.plusMillis(2000).toEpochMilli());
	request.setServerEndTime(1, now.plusMillis(2100).toEpochMilli());
	request.setProcessEndTime(now.plusMillis(2500).toEpochMilli());

	statistic.update(request);

	statistic.report();
	statistic.reset();

	assert (false);
	// assert statements
	// assertEquals(0, tester.multiply(10, 0), "10 x 0 must be 0");
	// assertEquals(0, tester.multiply(0, 10), "0 x 10 must be 0");
	// assertEquals(0, tester.multiply(0, 0), "0 x 0 must be 0");
    }

}
