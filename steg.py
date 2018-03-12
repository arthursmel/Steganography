

'''
 command line arguments

 steg ./carrier ./payload ./output
 steg ./input ./output 


- each payload bit needs 8 bits in the carrier
- 32 bits header containing number of bytes (max image size)
- 1 bit of payload per byte of carrier 
(payload_size * 8) + (32 * 8) < carrier_size



if carrier not big enough to carry payload
	exit

insert payload size into carrier (32) fixed

for each pixel in carrier
	r
	g
	b



for next 3 bits in payload, next pixel coords
	







func insertBytesIntoCarrier(bytes, carrier_bytes, curIndex)



	ret newIndex
'''
from itertools import izip
from PIL import Image
import math

class Steg:

	BITS_IN_BYTE = 8
	BYTES_IN_INTEGER = 4
	PRIMARY_COLOR_COUNT = 3

	def encode(self, carrier_path, payload_path, output_path):
	
		buf = Buffer()
		arr = []

		with open(payload_path, "rb") as p_img:
			f = p_img.read()
			payload_bytes = bytearray(f)

		with Image.open(carrier_path) as c_img:
			c_width, c_height = c_img.size
			c_img_pxs = c_img.load()

			self.create_length_header(payload_bytes)
			px_gen = self.generate_px_coord(c_width, c_height)
			bit_gen = self.generate_payload_bits(payload_bytes)

			for (x, y), byte in izip(px_gen, bit_gen):

				cur_px = c_img_pxs[x, y]
				new_px = self.get_encoded_px(cur_px, byte)
				c_img_pxs[x, y] = new_px

				b = buf.add_bits(self.get_decoded_px(new_px))
				if b != None:
					arr.append(b)


			c_img.save(output_path)

		for x in range(len(arr)):
			#print(arr[x], payload_bytes[x])
			pass



	def decode(self, encoded_path, output_path=None):
		
		
		with open("/Users/mel/Downloads/winflag.png", "rb") as p_img:
			f = p_img.read()
			payload_bytes = bytearray(f)

	
		with Image.open(encoded_path) as e_img:


			e_img_pxs = e_img.load()
			e_img_width, e_img_height = e_img.size

			for (a, b) in izip(self.generate_decoded_bytes(e_img_width, e_img_height, e_img_pxs), payload_bytes):
				print(a, b)
				pass



	def generate_decoded_bytes(self, e_img_width, e_img_height, e_img_pxs):

		PX_USED_FOR_HEADER = self.get_number_of_carrier_px(self.BYTES_IN_INTEGER)
		length = 0
		buf = Buffer()

		for (x, y) in self.generate_px_coord(e_img_width, e_img_height, end=PX_USED_FOR_HEADER):
			next_decoded_bits = self.get_decoded_px(e_img_pxs[x, y])
			next_decoded_byte = buf.add_bits(next_decoded_bits)
			if next_decoded_byte != None:
				length = self.add_byte_to_integer(length, next_decoded_byte)

		print(length, buf.buf)
		px_used_for_payload = self.get_number_of_carrier_px(length)

		for (x, y) in self.generate_px_coord(e_img_width, e_img_height,\
			start=PX_USED_FOR_HEADER, end=px_used_for_payload):
			next_decoded_bits = self.get_decoded_px(e_img_pxs[x, y])
			next_decoded_byte = buf.add_bits(next_decoded_bits)
			if next_decoded_byte != None:
				yield next_decoded_byte


	def create_length_header(self, payload_bytes):
		'''
		Creates a header in the byte array of the payload which contains the 
		length of the payload itself. The length is a 32 bit interger. The bytes 
		are inserted in the header from MS Byte -> LS Byte
		'''
		BYTE_MASK = 4278190080 # 1111 1111 0000 0000 0000 0000 0000 0000 
		length = len(payload_bytes) # The length of the payload to insert into header
		print(length)

		for byte_count in range(self.BYTES_IN_INTEGER):
			byte_to_insert = \
				(length & (BYTE_MASK >> (self.BITS_IN_BYTE * byte_count))) \
				>> ((self.BITS_IN_BYTE * (self.BYTES_IN_INTEGER - byte_count)) - self.BITS_IN_BYTE)
			payload_bytes.insert(byte_count, byte_to_insert)


	def generate_px_coord(self, width, height, start=None, end=None):
		end = (width * height) if not end else end
		cur_px = 0 if not start else start

		while cur_px < end:
			x = cur_px % width 
			y = cur_px // width
			cur_px += 1
			yield (x, y)


	def generate_payload_bits(self, payload_bytes):
		
		payload_bit_count = 0
		
		TOTAL_PAYLOAD_BITS = len(payload_bytes) * self.BITS_IN_BYTE
		PADDING = TOTAL_PAYLOAD_BITS % self.PRIMARY_COLOR_COUNT

		while payload_bit_count < TOTAL_PAYLOAD_BITS:

			cur_byte = 0
			bit_range = PADDING if \
				((TOTAL_PAYLOAD_BITS - payload_bit_count) < self.PRIMARY_COLOR_COUNT) \
				else self.PRIMARY_COLOR_COUNT

			for i in range(bit_range):

				cur_payload_byte = payload_bit_count // self.BITS_IN_BYTE
				cur_payload_bit = (self.BITS_IN_BYTE - (payload_bit_count % self.BITS_IN_BYTE)) - 1

				cur_bit = self.get_next_bit(payload_bytes[cur_payload_byte], cur_payload_bit)
 				cur_byte = self.add_bit_to_byte(cur_byte, cur_bit)

				payload_bit_count += 1

			yield cur_byte


	def get_next_bit(self, bits, shift_by):
		return (bits >> shift_by) & 1


	def add_bit_to_byte(self, cur_byte, bit_to_add):
		return (cur_byte << 1) | bit_to_add

	def add_byte_to_integer(self, integer, byte_to_add):
		return (integer << 8) | byte_to_add


	def get_encoded_px(self, px, byte):
		'''
		Takes a byte containing 3 lsb bits to be encoded
		as in the lsbs of an rgb pixel value
		Returns the modified rgb vales
		'''
		R_MASK = 4; R_POS = 2
		G_MASK = 2; G_POS = 1
		B_MASK = 1; B_POS = 0

		LSB_MASK = 1

		(r, g, b) = px
		r = (r & ~LSB_MASK) | ((byte & R_MASK) >> R_POS)
		g = (g & ~LSB_MASK) | ((byte & G_MASK) >> G_POS)
		b = (b & ~LSB_MASK) | ((byte & B_MASK) >> B_POS)

		return (r, g, b)


	def get_decoded_px(self, px):
		'''
		Return the LSB of the r, g, b values in the pixel
		'''
		(r, g, b) = px
		return [r % 2, g % 2, b % 2]


	def get_number_of_carrier_px(self, number_of_bytes):
		'''
		Calculate the number of pixels needed from the carrier to encode
		the payload image.
		'''
		return int(math.ceil((number_of_bytes * self.BITS_IN_BYTE) / float(self.PRIMARY_COLOR_COUNT)))


class Buffer: 

	BITS_IN_BYTE = 8
	buf = []

	def __init__(self):
		self.buf = []

	def add_bits(self, bits):
		buffered_byte = 0

		self.buf.extend(bits)
		if len(self.buf) >= self.BITS_IN_BYTE:
			return self.remove_byte()

	def remove_byte(self):
		byte = 0
		for bit in range(self.BITS_IN_BYTE):
			byte = (byte << 1) | self.buf.pop(0)
		return byte


if __name__ == '__main__':
	
	s = Steg()


	s.encode("/Users/mel/Downloads/iphone4scamera-111004-full.JPG", "/Users/mel/Downloads/winflag.png", "test.png")



	s.decode("test.png")



















