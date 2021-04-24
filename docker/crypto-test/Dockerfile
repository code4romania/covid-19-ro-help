# not "-alpine", because "cryptography" has no wheel for it, it tries to
# compile, wants rust, and fails.
FROM python:3.7.4

WORKDIR /build
ADD requirements-crypto*.txt ./
RUN pip install --upgrade pip \
	&& pip install -r requirements-crypto-test.txt

ADD ro_help ro_help/
# just verify imports
RUN python3 ro_help/mobilpay/mobilpay/util/encrypt_data.py
