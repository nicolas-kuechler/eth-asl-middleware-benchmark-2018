package ch.ethz.asl.kunicola.request;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public abstract class AbstractClientRequest {

    private final static Logger LOG = LogManager.getLogger();

    private String requestString;
    private SocketChannel client;

    // TODO [nku] add statistics

    // TODO [nku] here I need to give the socket connection and so on to the servers
    public void process() {
	beforeExecute();
	execute();
	afterExecute();
    }

    protected void beforeExecute() {

    }

    protected void execute() {
	LOG.info("Execute Request: {}", requestString);

	String answer = "STORED\r\n";
	ByteBuffer buffer = ByteBuffer.wrap(answer.getBytes());
	try {
	    while (buffer.hasRemaining()) {
		client.write(buffer);
	    }

	} catch (IOException e) {
	    e.printStackTrace();
	}
    }

    protected void afterExecute() {

    }

    public AbstractClientRequest withRequestString(String requestString) {
	this.requestString = requestString;
	return this;
    }

    public AbstractClientRequest with(SocketChannel client) {
	this.client = client;
	return this;
    }

}
