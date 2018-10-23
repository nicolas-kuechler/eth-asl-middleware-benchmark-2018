package ch.ethz.asl.kunicola.util;

import java.lang.Thread.UncaughtExceptionHandler;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class MiddlewareExceptionHandler implements UncaughtExceptionHandler {

    final static Logger LOG = LogManager.getLogger();

    @Override
    public void uncaughtException(Thread thread, Throwable e) {
	LOG.error("{} throws exception: {}", thread.getName(), e);
	// TODO [nku] decide if want to stop the system or restart thread

	Runtime.getRuntime().exit(-1);
    }

}
