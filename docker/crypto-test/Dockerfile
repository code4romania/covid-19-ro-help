# not "-alpine", because "cryptography" has no wheel for it, it tries to
# compile, wants rust, and fails.
FROM python:3.7.4

WORKDIR /build
ADD requirements-crypto*.txt ./
RUN pip install --upgrade pip \
	&& pip install -r requirements-crypto-test.txt

ADD docker/crypto-test/gen_testdata.sh .
RUN ./gen_testdata.sh

ADD ro_help/mobilpay mobilpay/
RUN pytest mobilpay/mobilpay/test.py -v
