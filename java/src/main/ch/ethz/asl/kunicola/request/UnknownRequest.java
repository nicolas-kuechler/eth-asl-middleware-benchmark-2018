package ch.ethz.asl.kunicola.request;

import java.nio.ByteBuffer;

import ch.ethz.asl.kunicola.util.ServerMessage;

public class UnknownRequest extends AbstractRequest {

	private String errorMsg;

	public UnknownRequest(byte[] content, String errorMsg) {
		super(content, "unknown", 1);
		setErrorMsg(errorMsg);
	}

	public String getErrorMsg() {
		return errorMsg;
	}

	public void setErrorMsg(String errorMsg) {
		this.errorMsg = errorMsg;
	}

	@Override
	public ServerMessage[] getServerMessages() {
		throw new IllegalArgumentException("UnknownRequest does not have server messages");
	}

	@Override
	public boolean putServerResponse(Integer serverId, ByteBuffer byteBuffer) {
		throw new IllegalArgumentException("UnknownRequest does not take server responses");
	}

}
