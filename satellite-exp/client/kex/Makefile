ROOT=$(shell dirname $(shell pwd))
OPENSSL_DIR=$(ROOT)/tmp/openssl

# Define OQS paths first
OQS_INCLUDE=$(OPENSSL_DIR)/oqs/include
OQS_LIB=$(OPENSSL_DIR)/oqs/lib

# Then use them in flags
CFLAGS=-g -Wall -Wextra -Werror -Wpedantic -I$(OPENSSL_DIR)/include -I$(OQS_INCLUDE)
LDFLAGS=-Wl,-rpath,$(OPENSSL_DIR) -L$(OPENSSL_DIR) -L$(OQS_LIB)
LIBS=-lssl -lcrypto -ldl -lpthread -loqs -lcjson

s_timer.o: s_timer.c
	$(CC) $(CFLAGS) $< $(LDFLAGS) $(LIBS) -o $@
