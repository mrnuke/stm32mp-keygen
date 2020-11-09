#! /usr/bin/env python3

""" ECDSA public key hashing tool

This tool is used to hash an ECDSA public key for consumption by STM32MP chips
using secure boot.
"""
import optparse
import sys
from Cryptodome.PublicKey import ECC
from Cryptodome.Hash import SHA256

def hash_pubkey(key, debug=False):
	""" Meat and potatoes of this program """
	coord_x_bytes = key.pointQ.x.to_bytes().rjust(32, b'\0')
	coord_y_bytes = key.pointQ.y.to_bytes().rjust(32, b'\0')
	raw_pubkey = coord_x_bytes + coord_y_bytes

	if debug:
		print('KEY on curve ' + key.curve)
		print('\tPoint X: ' + coord_x_bytes.hex())
		print('\tPoint Y: ' + coord_y_bytes.hex())

	return SHA256.new(data=raw_pubkey)

def main():
	""" Bacon wrapper function """
	parser = optparse.OptionParser()

	parser.add_option('-p', '--public-key', dest='pubkey',
			  help='PEM file containing the ECDSA public key')
	
	parser.add_option('-b', '--binhash-file', dest='hash_file',
			  help='Output file containing the SHA256 public key hash')

	parser.add_option('-d', '--debug', dest='debug', action="store_true",
			  help='Output debugging information')

	options, _ = parser.parse_args()

	if not options.pubkey:
		parser.print_help()
		print("Must specify public key file", file=sys.stderr)
		return 1

	with open(options.pubkey) as keyfile:
		key = ECC.import_key(keyfile.read())

	sha = hash_pubkey(key, options.debug)
	print(sha.hexdigest())

	if options.hash_file:
		with open(options.hash_file, 'wb') as hashfile:
			hashfile.write(sha.digest())

	return 0

if __name__ == '__main__':
		sys.exit(main())
