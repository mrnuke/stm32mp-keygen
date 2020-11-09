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
