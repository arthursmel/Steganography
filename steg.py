

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

class Steg:

	BITS_IN_BYTE = 8

	cur_pixel = 0

	payload_bit_count = 0
	payload_bytes = [1, 1, 255]

	carrier_height = 4
	carrier_width = 4

	def generate_pixel_coord(self, count=None):

		if not count:
			count = (self.carrier_height * self.carrier_width) \
					- self.cur_pixel

		while count > 0:
			x = self.cur_pixel % self.carrier_width 
			y = self.cur_pixel // self.carrier_height
			count -= 1
			self.cur_pixel += 1
			yield [y, x]


	def generate_next_bits(self):
		MASK = 1
		PRIMARY_COLOR_COUNT = 3
		TOTAL_PAYLOAD_BITS = len(self.payload_bytes) * self.BITS_IN_BYTE
		PADDING = TOTAL_PAYLOAD_BITS % PRIMARY_COLOR_COUNT

		while self.payload_bit_count < TOTAL_PAYLOAD_BITS:

			cur_bits = 0
			bit_range = PADDING if \
				((TOTAL_PAYLOAD_BITS - self.payload_bit_count) < PRIMARY_COLOR_COUNT) \
				else PRIMARY_COLOR_COUNT

			for i in range(bit_range):

				cur_payload_byte = self.payload_bit_count // self.BITS_IN_BYTE
				cur_payload_bit = self.payload_bit_count % self.BITS_IN_BYTE

				cur_bit = (self.payload_bytes[cur_payload_byte] >> cur_payload_bit) & MASK
 				cur_bits = self.add_bit_to_next_bits(cur_bits, cur_bit)

 				print cur_bit

				self.payload_bit_count += 1

			yield cur_bits


	def add_bit_to_next_bits(self, cur_bits, bit_to_add):
		# 0000 0000
		# 1st bit -> last bit
		return (cur_bits << 1) | bit_to_add




if __name__ == '__main__':
	
	s = Steg()

	for bits in s.generate_next_bits():
		print("Byte: " + str(bits))


	




















