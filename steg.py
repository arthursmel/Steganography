
from itertools import izip
from PIL import Image
import math
import sys

class Steg:

	BITS_IN_BYTE = 8
	BYTES_IN_INTEGER = 4
	PRIMARY_COLOR_COUNT = 3

	def encode(self, carrier_path, payload_path, output_path):
		'''
		Encodes the payload bytes into the carrier bytes
		'''
		with open(payload_path, "rb") as p_img:
			# Creating a byte array of the payload
			# so we can access each byte individually
			f = p_img.read()
			payload_bytes = bytearray(f)

		with Image.open(carrier_path) as c_img:
			# Opening the payload as an array of pixels
			# so we can access each pixel individually
			c_width, c_height = c_img.size
			c_img_pxs = c_img.load()

			# Creating the header in the payload byte array
			# which is a 32 bit integer of the number of bytes
			# in the payload excluding the header
			self.create_length_header(payload_bytes)

			px_gen = self.generate_px_coord(c_width, c_height)
			bit_gen = self.generate_payload_bits(payload_bytes)

			for (x, y), bits in izip(px_gen, bit_gen):
				# For each 3 bits in payload, and the pixel it 
				# will be encoded in

				cur_px = c_img_pxs[x, y] # Get the current pixel value
				# Encode the bits in the pixel lsb for each color
				new_px = self.get_encoded_px(cur_px, bits)
				c_img_pxs[x, y] = new_px # Update the pixel

			# Output updated image
			c_img.save(output_path)


	def decode(self, encoded_path, output_path):
		'''
		Decodes the payload bytes from the carrier bytes
		Creates a new file for the payload at output_path
		'''
		output_bytes = []
	
		with Image.open(encoded_path) as e_img:

			e_img_pxs = e_img.load()
			e_img_width, e_img_height = e_img.size

			for byte in self.generate_decoded_bytes(e_img_width, e_img_height, e_img_pxs):
				output_bytes.append(byte)
		
		with open(output_path, 'wb') as o_img:
   			o_img.write(bytearray(output_bytes))



	def generate_decoded_bytes(self, e_img_width, e_img_height, e_img_pxs):

		PX_USED_FOR_HEADER = self.get_number_of_carrier_px(self.BYTES_IN_INTEGER)
		length = 0
		buf = Buffer()

		for (x, y) in self.generate_px_coord(e_img_width, e_img_height, end=PX_USED_FOR_HEADER):
			next_decoded_bits = self.get_decoded_px(e_img_pxs[x, y])
			next_decoded_byte = buf.add_bits(next_decoded_bits)
			if next_decoded_byte != None:
				length = self.add_byte_to_integer(length, next_decoded_byte)

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
		BYTE_MASK = 255 << 24 # 1111 1111 0000 0000 0000 0000 0000 0000 
		length = len(payload_bytes) # The length of the payload to insert into header

		for byte_count in range(self.BYTES_IN_INTEGER):
			byte_to_insert = \
				(length & (BYTE_MASK >> (self.BITS_IN_BYTE * byte_count))) \
				>> ((self.BITS_IN_BYTE * (self.BYTES_IN_INTEGER - byte_count)) - self.BITS_IN_BYTE)
			payload_bytes.insert(byte_count, byte_to_insert)


	def generate_px_coord(self, width, height, start=None, end=None):
		'''
		Generates (x,y) co-ordinates for a 2d array, where the start
		value is the number of elements to skip at the start, and 
		the end value is the number of elements to skip at the end.
		'''
		end = (width * height) if not end else end
		cur_px = 0 if not start else start

		while cur_px < end:
			x = cur_px % width 
			y = cur_px // width
			cur_px += 1
			yield (x, y)


	def generate_payload_bits(self, payload_bytes):
		'''
		A generator which splits the payload_bytes into bytes which
		contain the information in only the LS 3 bits. This means these
		bytes can be used to easily encode the data in the rgb values 
		of pixels
		'''
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

		# Changing the LSB of each color component
		# to the associated bit of the byte to encode
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
	
	steg = Steg()
	arg_count = len(sys.argv)

	if (arg_count == 3):
		steg.decode(sys.argv[1], sys.argv[2])
	elif(arg_count == 4):
		steg.encode(sys.argv[1], sys.argv[2], sys.argv[3])
	else:
		print("python steg.py <carrier_path> <payload_path> <output_path>\npython steg.py <encoded_path> <output_path>")

