package ch.ethz.asl.kunicola.util;

import java.lang.Thread.UncaughtExceptionHandler;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Log any unhandled exception in the middleware and shutdown the middleware
 * 
 * @author nicolas-kuechler
 *
 */
public class MiddlewareExceptionHandler implements UncaughtExceptionHandler {

	final static Logger LOG = LogManager.getLogger();

	@Override
	public void uncaughtException(Thread thread, Throwable e) {
		LOG.error("{} throws exception: {}", thread.getName(), e);
		Runtime.getRuntime().exit(-1);
	}

}
