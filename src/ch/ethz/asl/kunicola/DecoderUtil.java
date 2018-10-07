package ch.ethz.asl.kunicola;

import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.Charset;
import java.nio.charset.CharsetDecoder;

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
