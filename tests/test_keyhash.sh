#! /bin/bash

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
KEYS_DIR="${SCRIPT_DIR}/keys"
: "${STM_KEYGEN_BIN:=${HOME}/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32MP_KeyGen_CLI}"
: "${KEYHASH_BIN:=${SCRIPT_DIR}/../ecdsa-sha256.py}"

generate_keys()
{
	for i in $(seq 1 1000); do
		local outdir="${KEYS_DIR}/key-$i"

		if [ -d "$outdir" ]; then
			continue
		fi

		yes | $STM_KEYGEN_BIN --absolute-path "$outdir" --password "nopass"
	done
}

test_keyhash()
{
	local keydir=$1

	genhash=$($KEYHASH_BIN --public-key="$keydir/publicKey.pem" \
			       --binhash-file="$keydir/generated-hash.bin")

	orighash=$(xxd -c32 -p "$keydir/publicKeyhash.bin")

	if [ "$genhash" != "$orighash" ]; then
		echo "ERROR: Derived hash in $keydir does not match"
	fi
}

test_key()
{
	local keydir=$1
	local genkey origkey

	genkey=$(openssl ec -in "$keydir/privateKey.pem" \
			-passin pass:nopass -pubout  2>/dev/null)

	origkey=$(cat "$keydir/publicKey.pem")

	if [ "$genkey" != "$origkey" ]; then
		echo "ERROR: Derived public key in $keydir does not match"
	fi
}

test_key_sequence()
{
	for i in $(seq 1 1000); do
		local keydir="${KEYS_DIR}/key-$i"

		test_key "$keydir"
		test_keyhash "$keydir"
	done
}

generate_keys
test_key_sequence
