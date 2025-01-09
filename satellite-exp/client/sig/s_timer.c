/*
 * Copyright 1995-2018 The OpenSSL Project Authors. All Rights Reserved.
 *
 * Licensed under the Apache License 2.0 (the "License").  You may not use
 * this file except in compliance with the License.  You can obtain a copy
 * in the file LICENSE in the source distribution or at
 * https://www.openssl.org/source/license.html
 */
#include <stdio.h>

#include <openssl/ssl.h>
#include <openssl/err.h>

#include <time.h>
#include <string.h>
#include <cjson/cJSON.h>

#define NS_IN_MS 1000000.0
#define MS_IN_S 1000

char* get_host_from_config(void) {
    // Read the file
    FILE* fp = fopen("../config.json", "r");
    if (!fp) {
        fprintf(stderr, "Error opening config file\n");
        return NULL;
    }

    // Get file size
    fseek(fp, 0, SEEK_END);
    long file_size = ftell(fp);
    rewind(fp);

    // Read file content
    char* json_string = malloc(file_size + 1);
    fread(json_string, 1, file_size, fp);
    json_string[file_size] = '\0';
    fclose(fp);

    // Parse JSON
    cJSON* root = cJSON_Parse(json_string);
    free(json_string);
    
    if (!root) {
        const char* error_ptr = cJSON_GetErrorPtr();
        if (error_ptr) {
            fprintf(stderr, "Error parsing JSON before: %s\n", error_ptr);
        }
        return NULL;
    }

    // Get values
    cJSON* server_ip = cJSON_GetObjectItem(root, "server_ip");
    cJSON* tls_port = cJSON_GetObjectItem(root, "tls_port");
    
    if (!cJSON_IsString(server_ip) || !cJSON_IsString(tls_port)) {
        fprintf(stderr, "Missing server_ip or tls_port in config\n");
        cJSON_Delete(root);
        return NULL;
    }

    // Combine host and port
    char* host = malloc(strlen(server_ip->valuestring) + strlen(tls_port->valuestring) + 2);
    sprintf(host, "%s:%s", server_ip->valuestring, tls_port->valuestring);
    
    cJSON_Delete(root);
    return host;
}

SSL* do_tls_handshake(SSL_CTX* ssl_ctx, const char* host)
{
    BIO* conn;
    SSL* ssl;
    int ret;

    conn = BIO_new(BIO_s_connect());
    if (!conn)
    {
        return 0;
    }

    BIO_set_conn_hostname(conn, host);
    BIO_set_conn_mode(conn, BIO_SOCK_NODELAY);

    ssl = SSL_new(ssl_ctx);

    SSL_set_bio(ssl, conn, conn);

    /* ok, lets connect */
    ret = SSL_connect(ssl);
    if (ret <= 0)
    {
        ERR_print_errors_fp(stderr);
        SSL_free(ssl);
        return 0;
    }

#if defined(SOL_SOCKET) && defined(SO_LINGER)
    {
        struct linger no_linger = {.l_onoff = 1, .l_linger = 0};
        int fd = SSL_get_fd(ssl);
        if (fd >= 0)
        {
            (void)setsockopt(fd, SOL_SOCKET, SO_LINGER, (char*)&no_linger,
                             sizeof(no_linger));
        }
    }
#endif
    return ssl;
}

int main(int argc, char* argv[])
{
    int ret = -1;
    SSL_CTX* ssl_ctx = 0;
    if(argc != 3)
    {
        fprintf(stderr, "Wrong number of arguments.\n");
        goto end;
    }
    const size_t measurements_to_make = strtol(argv[2], 0, 10);
    size_t measurements = 0;

    // const char* sig_alg = argv[1];
    // char CA_cert[100] = { 0 };

    const char* sig_alg = argv[1];
    char CA_cert[100] = { 0 };
    snprintf(CA_cert, 100, "./%s_CA.crt", sig_alg);

    const char* ciphersuites = "TLS_AES_256_GCM_SHA384";
    const SSL_METHOD* ssl_meth = TLS_client_method();
    SSL* ssl = NULL;

    struct timespec start, finish;
    double* handshake_times_ms = malloc(measurements_to_make * sizeof(*handshake_times_ms));

    ssl_ctx = SSL_CTX_new(ssl_meth);
    if (!ssl_ctx)
    {
        goto ossl_error;
    }

    SSL_CTX_set_mode(ssl_ctx, SSL_MODE_AUTO_RETRY);
    SSL_CTX_set_quiet_shutdown(ssl_ctx, 1);

    ret = SSL_CTX_set_min_proto_version(ssl_ctx, TLS1_3_VERSION);
    if (ret != 1)
    {
        goto ossl_error;
    }

    ret = SSL_CTX_set_max_proto_version(ssl_ctx, TLS1_3_VERSION);
    if (ret != 1)
    {
        goto ossl_error;
    }

    SSL_CTX_set_options(ssl_ctx, SSL_OP_NO_COMPRESSION);

    ret = SSL_CTX_set_ciphersuites(ssl_ctx, ciphersuites);
    if (ret != 1)
    {
        goto ossl_error;
    }
    ret = SSL_CTX_set1_groups_list(ssl_ctx, "p256_kyber512_90s");
    if (ret != 1)
    {
        goto ossl_error;
    }

    ret = SSL_CTX_load_verify_locations(ssl_ctx, CA_cert, 0);
    if(ret <= 0)
    {
        goto ossl_error;
    }
    SSL_CTX_set_verify(ssl_ctx, SSL_VERIFY_PEER, NULL);

    char* host = get_host_from_config();
    if (!host) {
        fprintf(stderr, "Failed to get host from config\n");
        goto end;
    }

    while(measurements < measurements_to_make)
    {
        clock_gettime(CLOCK_MONOTONIC_RAW, &start);
        ssl = do_tls_handshake(ssl_ctx, host);
        clock_gettime(CLOCK_MONOTONIC_RAW, &finish);
        if (!ssl)
        {
            /* Retry since at high packet loss rates,
             * the connect() syscall fails sometimes.
             * Non-retryable errors are caught by manual
             * inspection of logs, which has sufficed
             * for our purposes */
            continue;
        }

        SSL_set_shutdown(ssl, SSL_SENT_SHUTDOWN | SSL_RECEIVED_SHUTDOWN);
        ret = BIO_closesocket(SSL_get_fd(ssl));
        if(ret == -1)
        {
            goto ossl_error;
        }

        SSL_free(ssl);

        handshake_times_ms[measurements] = ((finish.tv_sec - start.tv_sec) * MS_IN_S) + ((finish.tv_nsec - start.tv_nsec) / NS_IN_MS);
        measurements++;
    }

    for(size_t i = 0; i < measurements; i++)
    {
        printf("%f,", handshake_times_ms[i]);
    }
    // printf("%f", handshake_times_ms[measurements - 1]);
    printf("\n");

    ret = 0;
    goto end;

ossl_error:
    fprintf(stderr, "Unrecoverable OpenSSL error.\n");
    ERR_print_errors_fp(stderr);
end:
    SSL_CTX_free(ssl_ctx);
    free(host);
    return ret;
}
