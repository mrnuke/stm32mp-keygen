# stm32mp-keygen

A key generation utility for STM32MP SOCs.

## Generating keys

This package does not provide an explicit method of generating ECDSA keys. Keys
can be generated with the __openssl__ package:

	$ openssl ecparam -name prime256v1 -genkey -out <private_key.pem>
	$ openssl ec -in <private_key.pem> -pubout -out <public_key.pem>

### Generating the key hashes

In order to be used by the STM32MP secure boot, the public key must be hashed.
The __ecdsa-sha256.py__ is provided for this purpose:

	$ ./ecdsa-sha256.py --public-key=<public_key.pem> --binhash-file=<hash.bin>

## Signing and veryfying images

STM32 images can be checked and signed with __stm32-sign.py__. Note that images
must already have an STM32 header (e.g. u-boot-spl.stm32).

	$ ./stm32-sign.py --help
	$ ./stm32-sign.py --key-file <public_key.pem> --verify <image.stm32>

To sign an STM32 image:

	$ ./stm32-sign.py --key-file <private_key.pem> --sign <image.stm32> --output <image-signed.stm32>


## Developer tools

### Testing utilities

#### Binary hash testing

The hash generation can be tested with __tests/test_keyhash.sh__. This tool
compares the output of the key hashing utility to the _official_ STM tool. It
marks failing hashes for further analysis.

	$ tests/test_keyhash.sh

It can be massaged with the following environment variables:

  * __STM_KEYGEN_BIN__ - Location __STM32MP_KeyGen_CLI__ binary
  * __KEYHASH_BIN__ - Location of __ecdsa-sha256.py__ tool
