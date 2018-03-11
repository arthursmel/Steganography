

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

	def encode(self, carrier_path, payload_path):
	
		with open(payload_path, "rb") as p_img:
			f = p_img.read()
			payload_bytes = bytearray(f)

		with Image.open(carrier_path) as c_img:
			c_width, c_height = c_img.size
			c_img_pxs = c_img.load()

			self.create_length_header(payload_bytes)
			px_needed = self.get_number_of_carrier_px(payload_bytes)
			px_gen = self.generate_px_coord(c_width, c_height)
			bit_gen = self.generate_payload_bits(payload_bytes)

			for (x, y), byte in izip(px_gen, bit_gen):

				cur_px = c_img_pxs[x, y]
				new_px = self.get_encoded_px(cur_px, byte)
				c_img_pxs[x, y] = new_px


			c_img.save('test.jpg')


	def decode(self, encoded_path):
		pass



	def create_length_header(self, payload_bytes):
		'''
		Creates a header in the byte array of the payload which contains the 
		length of the payload itself. The length is a 32 bit interger. The bytes 
		are inserted in the header from LS Byte -> MS Byte
		'''
		BYTE_MASK = 255 # 0000 0000 0000 0000 0000 0000 1111 1111
		length = len(payload_bytes) # The length of the payload to insert into header

		for byte_count in range(self.BYTES_IN_INTEGER):
			byte_to_insert = \
				(length & (BYTE_MASK << (self.BITS_IN_BYTE * byte_count))) \
				>> (self.BITS_IN_BYTE * byte_count)
			payload_bytes.insert(byte_count, byte_to_insert)


	def generate_px_coord(self, width, height):
		TOTAL_PIXELS = width * height
		cur_px = 0

		while cur_px < TOTAL_PIXELS:
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
				cur_payload_bit = payload_bit_count % self.BITS_IN_BYTE

				cur_bit = self.get_next_bit(payload_bytes[cur_payload_byte], cur_payload_bit)
 				cur_byte = self.add_bit_to_byte(cur_byte, cur_bit)

				payload_bit_count += 1

			yield cur_byte


	def get_next_bit(self, bits, shift_by):
		return (bits >> shift_by) & 1


	def add_bit_to_byte(self, cur_byte, bit_to_add):
		return (cur_byte << 1) | bit_to_add


	def get_encoded_px(self, px, byte):
		R_MASK = 4; R_POS = 2
		G_MASK = 2; G_POS = 1
		B_MASK = 1; B_POS = 0

		LSB_MASK = 1

		(r, g, b) = px
		r = (r & ~LSB_MASK) | ((byte & R_MASK) >> R_POS)
		g = (g & ~LSB_MASK) | ((byte & G_MASK) >> G_POS)
		b = (b & ~LSB_MASK) | ((byte & B_MASK) >> B_POS)

		return (r, g, b)

	def get_number_of_carrier_px(self, payload_bytes):
		'''
		Calculate the number of pixels needed from the carrier to encode
		the payload image.
		'''
		return int(math.ceil((len(payload_bytes) * self.BITS_IN_BYTE) / float(self.PRIMARY_COLOR_COUNT)))





if __name__ == '__main__':
	
	s = Steg()
	s.encode("/Users/mel/Downloads/iphone4scamera-111004-full.JPG", "/Users/mel/Downloads/I86rTVl.jpg")

	'''
	px_gen = s.generate_px_coord(2)
	bit_gen = s.generate_payload_bits()

	for (x, y), byte in izip(px_gen, bit_gen):
		print("Byte: " + str(byte) + ", pix: " + str(x) + str(y))
	'''






















