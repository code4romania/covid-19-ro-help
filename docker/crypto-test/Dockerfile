# not "-alpine", because "cryptography" has no wheel for it, it tries to
# compile, wants rust, and fails.
FROM python:3.7.4

WORKDIR /build
ADD requirements-crypto*.txt ./
RUN pip install --upgrade pip \
	&& pip install -r requirements-crypto-test.txt

RUN \
	for size in 1024 ; do \
		for side in us them ; do \
			d=pki/${side}-rsa${size} ; \
			mkdir -p $d ; \
			openssl genrsa -out $d/private.pem $size ; \
			openssl req \
				-x509 \
				-key $d/private.pem \
				-out $d/public.pem \
				-subj "/OU=test/CN=$side" \
				-days 36525 ; \
		done ; \
	done


ADD ro_help/mobilpay mobilpay/
# just verify imports
RUN python3 mobilpay/mobilpay/util/encrypt_data.py
