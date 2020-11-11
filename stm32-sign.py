#! /usr/bin/env python3

import logging
import optparse
import sys
import struct
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import ECC
from Cryptodome.Signature import DSS

def get_raw_pubkey(key):
	coord_x_bytes = key.pointQ.x.to_bytes().rjust(32, b'\0')
	coord_y_bytes = key.pointQ.y.to_bytes().rjust(32, b'\0')
	return coord_x_bytes + coord_y_bytes


def unpack_header(bindat):

	fmt = '<4s64s10I64s83xB'
	d = struct.unpack(fmt, bindat[0:256])

	stm32 = {}
	stm32['magic']		= d[0]
	stm32['signature'] 	= d[1]
	stm32['checksum'] 	= d[2]
	stm32['hdr_version']	= d[3]
	stm32['length']		= d[4]
	stm32['entry_addr']	= d[5]
	stm32['load_addr']	= d[7]
	stm32['hdr_version']	= d[9]
	stm32['oflags']		= d[10]
	stm32['ecdsa_algo']	= d[11]
	stm32['ecdsa_pubkey']	= d[12]

	return stm32


def verify_signature(bindat, key):

	hdr = unpack_header(bindat)
	signature = hdr['signature']
	image_pubkey = hdr['ecdsa_pubkey']
	raw_pubkey = get_raw_pubkey(key)

	if raw_pubkey != image_pubkey:
		print('Image is not signed with the provided key')
		return 1

	sha = SHA256.new(bindat[0x48:])
	verifier = DSS.new(key, 'fips-186-3')

	try:
		verifier.verify(sha, signature)
		log.info('Signature checks out')

	except ValueError:
		log.error('The signature is fake news')
		log.error('Found:    ' +  signature.hex())
		return 2

	return 0


def main():
	global log
	log = logging.getLogger(sys.argv[0])
	log.addHandler(logging.StreamHandler())
	parser = optparse.OptionParser()

	parser.add_option('-k', '--key-file', dest = 'key_file',
		help = 'PEM file containing the ECDSA key')

	parser.add_option('-v', '--verbose', dest = 'verbose', action="store_true",
		help = 'Output informative messages')

	parser.add_option('-d', '--debug', dest = 'debug', action="store_true",
		help = 'Output debugging information')

	parser.add_option('-e', '--verify', dest = 'verify_file',
		help = 'Verify signature of STM32 image')

	options, args = parser.parse_args()

	if not options.key_file:
		parser.print_help()
		log.error("Must specify a key file")
		return 1

	if options.debug:
		log.setLevel(logging.DEBUG)
	elif options.verbose:
		log.setLevel('INFO')

	f = open(options.key_file)
	key = ECC.import_key(f.read(), passphrase='nopass')


	if options.verify_file:
		try:
			g = open(options.verify_file, 'rb')
			verify_signature(g.read(), key)
			return 0
		except OSError as e:
			log.error("Can't open " + options.verify_file)
			return e.errno

	return 0

if __name__ == '__main__':
	ret = main()
	sys.exit(ret)
