package ch.ethz.asl.kunicola;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import java.io.UnsupportedEncodingException;
import java.nio.ByteBuffer;
import java.util.Arrays;

import org.junit.BeforeClass;
import org.junit.Test;

import ch.ethz.asl.kunicola.request.AbstractRequest;
import ch.ethz.asl.kunicola.thread.NetThread;
import ch.ethz.asl.kunicola.util.RequestDecoder;
import ch.ethz.asl.kunicola.util.DecoderUtil;
import ch.ethz.asl.kunicola.util.ServerMessage;

public class RequestDecoderTest {

	static int numberOfServers;
	static RequestDecoder decoder;

	@BeforeClass
	public static void init() {
		numberOfServers = 3;
		decoder = new RequestDecoder().withNumberOfServers(numberOfServers)
				.withShardedMultiGet(false);
	}

	@Test
	public void testSetStandard() {
		String cmd = String.format("set memtier-1023 0 0 4096\r\n%s\r\n", getDataBlock(4096));

		ByteBuffer buffer = toByteBuffer(cmd);
		AbstractRequest req = decoder.decode(buffer);
		assertFalse(decoder.hasMore());

		verifySet(req, cmd, numberOfServers);
	}

	@Test
	public void testSetNoReply() {
		String cmd = String.format("set memtier-1023 0 0 4096 noreply\r\n%s\r\n", getDataBlock(4096));

		ByteBuffer buffer = toByteBuffer(cmd);
		AbstractRequest req = decoder.decode(buffer);
		assertFalse(decoder.hasMore());

		verifySet(req, cmd, numberOfServers);
	}

	@Test
	public void testSetDelimiterInValue() {
		String cmd = String.format("set memtier-1023 0 0 4096\r\n%s\r\n",
				getDataBlock(2000) + "\r\n" + getDataBlock(2092) + "\r\n");

		ByteBuffer buffer = toByteBuffer(cmd);
		AbstractRequest req = decoder.decode(buffer);
		assertFalse(decoder.hasMore());

		verifySet(req, cmd, numberOfServers);
	}

	@Test
	public void testSetPartialInCmd1() {
		// first send incomplete request
		String cmd1 = String.format("set memtier-1023 0 0 409");
		ByteBuffer buffer1 = toByteBuffer(cmd1);
		int pos = buffer1.position();
		int limit = buffer1.limit();
		AbstractRequest req = decoder.decode(buffer1);
		assertFalse(decoder.hasMore());

		assertNull(req);
		assertEquals("buffer position", pos, buffer1.position());
		assertEquals("buffer limit", limit, buffer1.limit());

		// second send complete request
		String cmd2 = String.format("set memtier-1023 0 0 4096\r\n%s\r\n", getDataBlock(4096));
		ByteBuffer buffer2 = toByteBuffer(cmd2);

		AbstractRequest req2 = decoder.decode(buffer2);
		verifySet(req2, cmd2, numberOfServers);
	}

	@Test
	public void testSetPartialInCmd2() {
		// first send incomplete request
		String cmd1 = String.format("set memtier-1023 ");
		ByteBuffer buffer1 = toByteBuffer(cmd1);
		int pos = buffer1.position();
		int limit = buffer1.limit();
		AbstractRequest req = decoder.decode(buffer1);
		assertFalse(decoder.hasMore());

		assertNull(req);
		assertEquals("buffer position", pos, buffer1.position());
		assertEquals("buffer limit", limit, buffer1.limit());

		// second send complete request
		String cmd2 = String.format("set memtier-1023 0 0 4096\r\n%s\r\n", getDataBlock(4096));
		ByteBuffer buffer2 = toByteBuffer(cmd2);
		AbstractRequest req2 = decoder.decode(buffer2);
		assertFalse(decoder.hasMore());

		verifySet(req2, cmd2, numberOfServers);
	}

	@Test
	public void testSetPartialInValue() {
		// first send incomplete request
		String cmd1 = String.format("set memtier-1023 0 0 4096 noreply\r\n%s", getDataBlock(1023));
		ByteBuffer buffer1 = toByteBuffer(cmd1);
		int pos = buffer1.position();
		int limit = buffer1.limit();
		AbstractRequest req = decoder.decode(buffer1);
		assertFalse(decoder.hasMore());
		assertNull(req);
		assertEquals("buffer position", pos, buffer1.position());
		assertEquals("buffer limit", limit, buffer1.limit());

		// second send complete request
		String cmd2 = String.format("set memtier-1023 0 0 4096\r\n%s\r\n", getDataBlock(4096));
		ByteBuffer buffer2 = toByteBuffer(cmd2);
		AbstractRequest req2 = decoder.decode(buffer2);
		assertFalse(decoder.hasMore());
		verifySet(req2, cmd2, numberOfServers);
	}

	@Test
	public void testSetIncomplete1() {
		String cmd = String.format("set memtier-1023 0 4096 noreply\r\n%s", getDataBlock(4096));
		ByteBuffer buffer = toByteBuffer(cmd);
		AbstractRequest req = decoder.decode(buffer);
		assertFalse(decoder.hasMore());
		verifyUnknown(req, "set memtier-1023 0 4096 noreply\r\n");
	}

	@Test
	public void testSetIncomplete2() {
		String cmd = String.format("set memtier-1023 0 0 4096 0\r\n%s", getDataBlock(4096));
		ByteBuffer buffer = toByteBuffer(cmd);
		AbstractRequest req = decoder.decode(buffer);
		assertFalse(decoder.hasMore());
		verifyUnknown(req, "set memtier-1023 0 0 4096 0\r\n");
	}

	@Test
	public void testSetIncomplete3() {
		String cmd = String.format("set memtier-1023 0 10 0 4096\r\n%s", getDataBlock(4096));
		ByteBuffer buffer = toByteBuffer(cmd);
		AbstractRequest req = decoder.decode(buffer);
		assertFalse(decoder.hasMore());
		verifyUnknown(req, "set memtier-1023 0 10 0 4096\r\n");
	}

	@Test
	public void testSetIncomplete4() {
		String cmd = String.format("store memtier-1023 0 0 4096\r\n%s", getDataBlock(4096));
		ByteBuffer buffer = toByteBuffer(cmd);
		AbstractRequest req = decoder.decode(buffer);
		assertFalse(decoder.hasMore());
		verifyUnknown(req, "store memtier-1023 0 0 4096\r\n");
	}

	@Test
	public void testGetStandard() {
		String cmd = String.format("get memtier-1023\r\n");

		ByteBuffer buffer = toByteBuffer(cmd);

		RequestDecoder ownDecoder = new RequestDecoder().withNumberOfServers(numberOfServers)
				.withShardedMultiGet(false); // due to round robin

		AbstractRequest req = ownDecoder.decode(buffer);
		assertFalse(ownDecoder.hasMore());
		verifyGet(req, cmd, 0);
	}

	@Test
	public void testGetIncompleteStandard() {
		String cmd1 = String.format("get memtier-1023\n");

		ByteBuffer buffer1 = toByteBuffer(cmd1);
		AbstractRequest req1 = decoder.decode(buffer1);
		assertFalse(decoder.hasMore());
		assertNull(req1);

		String cmd2 = String.format("get memtier-1023\nblabla\n");

		ByteBuffer buffer2 = toByteBuffer(cmd2);
		AbstractRequest req2 = decoder.decode(buffer2);
		assertFalse(decoder.hasMore());
		verifyUnknown(req2, cmd2);
	}

	@Test
	public void testGetRoundRobin() {

		RequestDecoder ownDecoder = new RequestDecoder().withNumberOfServers(numberOfServers)
				.withShardedMultiGet(false); // due to round robin

		for (int i = 0; i < 5; i++) {
			String cmd = String.format("get memtier-1023\r\n");
			ByteBuffer buffer = toByteBuffer(cmd);
			AbstractRequest req = ownDecoder.decode(buffer);
			assertFalse(ownDecoder.hasMore());
			verifyGet(req, cmd, i % numberOfServers);
		}

	}

	@Test
	public void testNonShardedMGetStandard() {
		String cmd = String.format("get memtier-1023 memtier-1024 memtier-1025 memtier-1022\r\n");

		ByteBuffer buffer = toByteBuffer(cmd);

		RequestDecoder ownDecoder = new RequestDecoder().withNumberOfServers(numberOfServers)
				.withShardedMultiGet(false); // due to round robin

		AbstractRequest req = ownDecoder.decode(buffer);

		assertFalse(ownDecoder.hasMore());

		verifyNonShardedMGet(req, cmd, 0);
	}

	@Test
	public void testShardedMGetEqual() {
		String cmd = String.format("get memtier-1023 memtier-1024 memtier-1025\r\n");

		ByteBuffer buffer = toByteBuffer(cmd);

		RequestDecoder ownDecoder = new RequestDecoder().withNumberOfServers(numberOfServers)
				.withShardedMultiGet(true);

		AbstractRequest req = ownDecoder.decode(buffer);
		assertFalse(ownDecoder.hasMore());

		String[] cmds = {
				"get memtier-1023\r\n",
				"get memtier-1024\r\n",
				"get memtier-1025\r\n"
		};

		int[] serverIds = { 0, 1, 2 };

		verifyShardedMGet(req, cmd, cmds, serverIds);
	}

	@Test
	public void testShardedMGetUnequal() {
		String cmd = String.format("get memtier-1023 memtier-1024 memtier-1025 memtier-1026\r\n");

		ByteBuffer buffer = toByteBuffer(cmd);

		RequestDecoder ownDecoder = new RequestDecoder().withNumberOfServers(numberOfServers)
				.withShardedMultiGet(true);

		AbstractRequest req = ownDecoder.decode(buffer);
		assertFalse(ownDecoder.hasMore());

		String[] cmds = {
				"get memtier-1023 memtier-1024\r\n",
				"get memtier-1025\r\n",
				"get memtier-1026\r\n"
		};

		int[] serverIds = { 0, 1, 2 };

		verifyShardedMGet(req, cmd, cmds, serverIds);
	}

	@Test
	public void testShardedMGetLessThanServer() {
		String cmd = String.format("get memtier-1023 memtier-1024\r\n");

		ByteBuffer buffer = toByteBuffer(cmd);

		RequestDecoder ownDecoder = new RequestDecoder().withNumberOfServers(numberOfServers)
				.withShardedMultiGet(true);

		AbstractRequest req = ownDecoder.decode(buffer);

		assertFalse(ownDecoder.hasMore());

		String[] cmds = {
				"get memtier-1023\r\n",
				"get memtier-1024\r\n"
		};

		int[] serverIds = { 0, 1 };

		verifyShardedMGet(req, cmd, cmds, serverIds);
	}

	@Test
	public void testDoubleCommand() {
		String cmd = String.format("get memtier-1023 memtier-1024\r\nget memtier-1000\r\n");

		ByteBuffer buffer = toByteBuffer(cmd);

		RequestDecoder ownDecoder = new RequestDecoder().withNumberOfServers(numberOfServers)
				.withShardedMultiGet(false);

		AbstractRequest req1 = ownDecoder.decode(buffer);
		verifyNonShardedMGet(req1, "get memtier-1023 memtier-1024\r\n", 0);

		assertTrue(ownDecoder.hasMore());

		AbstractRequest req2 = ownDecoder.decode(buffer);
		verifyGet(req2, "get memtier-1000\r\n", 1);
	}

	private void verifySet(AbstractRequest req, String cmd, int numberOfServers) {
		assertNotNull(req);
		assertEquals("request type", "set", req.getType());
		assertEquals("content", cmd, DecoderUtil.decode(req.getContent()));

		ServerMessage[] msgs = req.getServerMessages();
		assertEquals("msgs length", numberOfServers, msgs.length);

		for (int i = 0; i < msgs.length; i++) {
			assertEquals("msg server id", i, msgs[i].getServerId());
			assertEquals("msg content", cmd, DecoderUtil.decode(msgs[i].getContent()));
		}
	}

	private void verifyGet(AbstractRequest req, String cmd, int serverId) {
		assertNotNull(req);
		assertEquals("request type", "get", req.getType());
		assertEquals("content", cmd, DecoderUtil.decode(req.getContent()));

		ServerMessage[] msgs = req.getServerMessages();
		assertEquals("msgs length", 1, msgs.length);

		for (int i = 0; i < msgs.length; i++) {
			assertEquals("msg server id", serverId, msgs[i].getServerId());
			assertEquals("msg content", cmd, DecoderUtil.decode(msgs[i].getContent()));
		}
	}

	private void verifyNonShardedMGet(AbstractRequest req, String cmd, int serverId) {
		assertNotNull(req);
		assertEquals("request type", "mget", req.getType());
		assertEquals("content", cmd, DecoderUtil.decode(req.getContent()));

		ServerMessage[] msgs = req.getServerMessages();
		assertEquals("msgs length", 1, msgs.length);

		for (int i = 0; i < msgs.length; i++) {
			assertEquals("msg server id", serverId, msgs[i].getServerId());
			assertEquals("msg content", cmd, DecoderUtil.decode(msgs[i].getContent()));
		}
	}

	private void verifyShardedMGet(AbstractRequest req, String cmd, String[] cmds, int[] serverIds) {
		assertNotNull(req);
		assertEquals("request type", "mget", req.getType());
		assertEquals("content", cmd, DecoderUtil.decode(req.getContent()));

		ServerMessage[] msgs = req.getServerMessages();
		assertEquals("msgs length", serverIds.length, msgs.length);

		for (int i = 0; i < msgs.length; i++) {
			assertEquals("msg server id", serverIds[i], msgs[i].getServerId());
			assertEquals("msg content", cmds[i], DecoderUtil.decode(msgs[i].getContent()));
		}
	}

	private void verifyUnknown(AbstractRequest req, String cmd) {
		assertNotNull(req);
		assertEquals("request type", "unknown", req.getType());
		assertEquals("content", cmd, DecoderUtil.decode(req.getContent()));
	}

	private String getDataBlock(int length) {
		char[] chars = new char[length];
		Arrays.fill(chars, 'x');
		return new String(chars);
	}

	private ByteBuffer toByteBuffer(String cmd) {
		ByteBuffer buffer = ByteBuffer.allocate(NetThread.BUFFER_SIZE);
		try {
			buffer.put(cmd.getBytes("UTF-8"));
		} catch (UnsupportedEncodingException e) {
			throw new IllegalArgumentException("Cannot Encode Cmd");
		}
		return buffer;
	}

}
