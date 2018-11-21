package ch.ethz.asl.kunicola.util;

/**
 * Exception that is thrown when an illegal request is detected in the decoding
 * 
 * @author nicolas-kuechler
 *
 */
public class IllegalRequestException extends Exception {

	private static final long serialVersionUID = 1L;

	public IllegalRequestException() {
		super();
	}

	public IllegalRequestException(String arg0, Throwable arg1, boolean arg2, boolean arg3) {
		super(arg0, arg1, arg2, arg3);
	}

	public IllegalRequestException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

	public IllegalRequestException(String arg0) {
		super(arg0);
	}

	public IllegalRequestException(Throwable arg0) {
		super(arg0);
	}

}
