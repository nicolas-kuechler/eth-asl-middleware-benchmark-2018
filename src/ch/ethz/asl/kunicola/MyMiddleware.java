package ch.ethz.asl.kunicola;

import java.io.IOException;
import java.util.List;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;


public class MyMiddleware {
	
	final static Logger logger = LogManager.getLogger();
	
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
		logger.info("Middleware Started: " + this);
	}


	@Override
	public String toString() {
		return "MyMiddleware [myIp=" + myIp + ", myPort=" + myPort + ", mcAddresses=" + mcAddresses + ", numThreadsPTP="
				+ numThreadsPTP + ", readSharded=" + readSharded + "]";
	}
	
}
