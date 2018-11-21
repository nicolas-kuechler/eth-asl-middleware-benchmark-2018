package ch.ethz.asl.kunicola.util;

import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.Charset;
import java.nio.charset.CharsetDecoder;

/**
 * Utility class for debugging that allows to decode a byte array and a
 * ByteBuffer without changing its limit and position.
 * 
 * @author nicolas-kuechler
 *
 */
public class DecoderUtil {

	private static final CharsetDecoder DECODER = Charset.forName("UTF8").newDecoder();

	private DecoderUtil() {
	}

	public static String decode(ByteBuffer buffer) {

		String s = null;
		int pos = buffer.position();
		int limit = buffer.limit();
		buffer.flip();
		try {
			s = DECODER.decode(buffer).toString();
		} catch (CharacterCodingException e) {
			// do nothing
		}
		buffer.position(pos);
		buffer.limit(limit);

		return s;

	}

	public static String decode(byte[] content) {
		return new String(content);
	}

}
