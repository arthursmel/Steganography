# Steganography

[Hides a picture in a picture](https://en.wikipedia.org/wiki/Steganography)

## Usage
### Encoding 
`python steg.py <carrier_path> <payload_path> <output_path>`
### Decoding
`python steg.py <input_path> <output_path>`

## Todo

* Comments
* Clean up code
* Currently only works if the encoded file is .png
* Error handling
  * If carrier is too small for payload
