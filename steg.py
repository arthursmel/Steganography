

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

class Steg:

	BITS_IN_BYTE = 8
	BYTES_IN_INTEGER = 4

	payload_bit_count = 0
	payload_bytes = [1, 1, 1, 255]

	carrier_height = 4
	carrier_width = 4

	def __init__(self):
		pass




	def create_length_header(self, payload_bytes):
		'''
		Creates a header in the byte array of the payload which contains the 
		length of the payload itself. The length is a 32 bit interger. The bytes 
		are inserted in the header from LSB -> MSB
		'''
		BYTE_MASK = 255 # 0000 0000 0000 0000 0000 0000 1111 1111
		length = len(payload_bytes) # The length of the payload to insert into header

		for byte_count in range(self.BYTES_IN_INTEGER):
			byte_to_insert = \
				(length & (BYTE_MASK << (self.BITS_IN_BYTE * byte_count))) \
				>> (self.BITS_IN_BYTE * byte_count)
			payload_bytes.insert(byte_count, byte_to_insert)


	def generate_px_coord(self, start, end, width, height):
		TOTAL_PIXELS = width * height
		cur_pixel = start

		while cur_pixel < end:
			x = cur_pixel % width 
			y = cur_pixel // height
			cur_pixel += 1
			yield (x, y)


	def generate_payload_bits(self):
		
		PRIMARY_COLOR_COUNT = 3
		TOTAL_PAYLOAD_BITS = len(self.payload_bytes) * self.BITS_IN_BYTE
		PADDING = TOTAL_PAYLOAD_BITS % PRIMARY_COLOR_COUNT

		while self.payload_bit_count < TOTAL_PAYLOAD_BITS:

			cur_byte = 0
			bit_range = PADDING if \
				((TOTAL_PAYLOAD_BITS - self.payload_bit_count) < PRIMARY_COLOR_COUNT) \
				else PRIMARY_COLOR_COUNT

			for i in range(bit_range):

				cur_payload_byte = self.payload_bit_count // self.BITS_IN_BYTE
				cur_payload_bit = self.payload_bit_count % self.BITS_IN_BYTE

				cur_bit = self.get_next_bit(self.payload_bytes[cur_payload_byte], cur_payload_bit)
 				cur_byte = self.add_bit_to_byte(cur_byte, cur_bit)

				self.payload_bit_count += 1

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




if __name__ == '__main__':
	
	s = Steg()

	pl = [1] * 2
	s.create_length_header(pl)
	print pl

	'''
	px_gen = s.generate_px_coord(2)
	bit_gen = s.generate_payload_bits()

	for (x, y), byte in izip(px_gen, bit_gen):
		print("Byte: " + str(byte) + ", pix: " + str(x) + str(y))
	'''






















