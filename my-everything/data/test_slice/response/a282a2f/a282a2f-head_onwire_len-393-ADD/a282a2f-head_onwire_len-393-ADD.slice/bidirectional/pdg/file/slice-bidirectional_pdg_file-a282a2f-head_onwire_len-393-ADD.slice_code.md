### File: `code/code_new/net/ceph/messenger_v2.c`

#### Function: `static int prepare_hello(struct ceph_connection *con)`

```c
L1267: static int prepare_hello(struct ceph_connection *con)
L1272: 	ctrl_len = 1 + ceph_entity_addr_encoding_len(&con->peer_addr);
L1273: 	buf = alloc_conn_buf(con, head_onwire_len(ctrl_len, false));
```

#### Function: `static int prepare_auth_request(struct ceph_connection *con)`

```c
L1289: static int prepare_auth_request(struct ceph_connection *con)
L1296: 	ctrl_len = AUTH_BUF_LEN;
L1297: 	buf = alloc_conn_buf(con, head_onwire_len(ctrl_len, false));
```

#### Function: `static int prepare_auth_request_more(struct ceph_connection *con,`

```c
L1325: static int prepare_auth_request_more(struct ceph_connection *con,
L1333: 	ctrl_len = AUTH_BUF_LEN;
L1334: 	buf = alloc_conn_buf(con, head_onwire_len(ctrl_len, false));
```

#### Function: `static int prepare_auth_signature(struct ceph_connection *con)`

```c
L1357: static int prepare_auth_signature(struct ceph_connection *con)
L1362: 	buf = alloc_conn_buf(con, head_onwire_len(SHA256_DIGEST_SIZE,
L1363: 						  con_secure(con)));
```

#### Function: `static int prepare_client_ident(struct ceph_connection *con)`

```c
L1376: static int prepare_client_ident(struct ceph_connection *con)
L1378: 	struct ceph_entity_addr *my_addr = &con->msgr->inst.addr;
L1379: 	struct ceph_client *client = from_msgr(con->msgr);
L1380: 	u64 global_id = ceph_client_gid(client);
L1388: 	if (!con->v2.client_cookie) {
L1390: 			get_random_bytes(&con->v2.client_cookie,
L1391: 					 sizeof(con->v2.client_cookie));
L1392: 		} while (!con->v2.client_cookie);
L1393: 		dout("%s con %p generated cookie 0x%llx\n", __func__, con,
L1394: 		     con->v2.client_cookie);
L1396: 		dout("%s con %p cookie already set 0x%llx\n", __func__, con,
L1397: 		     con->v2.client_cookie);
L1400: 	dout("%s con %p my_addr %s/%u peer_addr %s/%u global_id %llu global_seq %llu features 0x%llx required_features 0x%llx cookie 0x%llx\n",
L1401: 	     __func__, con, ceph_pr_addr(my_addr), le32_to_cpu(my_addr->nonce),
L1402: 	     ceph_pr_addr(&con->peer_addr), le32_to_cpu(con->peer_addr.nonce),
L1403: 	     global_id, con->v2.global_seq, client->supported_features,
L1404: 	     client->required_features, con->v2.client_cookie);
L1406: 	ctrl_len = 1 + 4 + ceph_entity_addr_encoding_len(my_addr) +
L1407: 		   ceph_entity_addr_encoding_len(&con->peer_addr) + 6 * 8;
L1408: 	buf = alloc_conn_buf(con, head_onwire_len(ctrl_len, con_secure(con)));
```

#### Function: `static int prepare_session_reconnect(struct ceph_connection *con)`

```c
L1428: static int prepare_session_reconnect(struct ceph_connection *con)
L1430: 	struct ceph_entity_addr *my_addr = &con->msgr->inst.addr;
L1434: 	WARN_ON(!con->v2.client_cookie);
L1435: 	WARN_ON(!con->v2.server_cookie);
L1436: 	WARN_ON(!con->v2.connect_seq);
L1439: 	dout("%s con %p my_addr %s/%u client_cookie 0x%llx server_cookie 0x%llx global_seq %llu connect_seq %llu in_seq %llu\n",
L1440: 	     __func__, con, ceph_pr_addr(my_addr), le32_to_cpu(my_addr->nonce),
L1441: 	     con->v2.client_cookie, con->v2.server_cookie, con->v2.global_seq,
L1442: 	     con->v2.connect_seq, con->in_seq);
L1444: 	ctrl_len = 1 + 4 + ceph_entity_addr_encoding_len(my_addr) + 5 * 8;
L1445: 	buf = alloc_conn_buf(con, head_onwire_len(ctrl_len, con_secure(con)));
```

#### Function: `static int prepare_read_control(struct ceph_connection *con)`

```c
L1706: static int prepare_read_control(struct ceph_connection *con)
L1708: 	int ctrl_len = con->v2.in_desc.fd_lens[0];
L1712: 	reset_in_kvecs(con);
L1713: 	if (con->state == CEPH_CON_S_V2_HELLO ||
L1714: 	    con->state == CEPH_CON_S_V2_AUTH) {
L1715: 		head_len = head_onwire_len(ctrl_len, false);
```

#### Function: `static int process_banner_payload(struct ceph_connection *con)`

```c
L1955: static int process_banner_payload(struct ceph_connection *con)
L1957: 	void *end = con->v2.in_kvecs[0].iov_base + con->v2.in_kvecs[0].iov_len;
L1958: 	u64 feat = CEPH_MSGR2_SUPPORTED_FEATURES;
L1959: 	u64 req_feat = CEPH_MSGR2_REQUIRED_FEATURES;
L1964: 	p = con->v2.in_kvecs[0].iov_base;
L1965: 	ceph_decode_64_safe(&p, end, server_feat, bad);
L1966: 	ceph_decode_64_safe(&p, end, server_req_feat, bad);
L1968: 	dout("%s con %p server_feat 0x%llx server_req_feat 0x%llx\n",
L1969: 	     __func__, con, server_feat, server_req_feat);
L1971: 	if (req_feat & ~server_feat) {
L1977: 	if (server_req_feat & ~feat) {
L1985: 	ret = prepare_hello(con);
```

#### Function: `static int process_hello(struct ceph_connection *con, void *p, void *end)`

```c
L2000: static int process_hello(struct ceph_connection *con, void *p, void *end)
L2002: 	struct ceph_entity_addr *my_addr = &con->msgr->inst.addr;
L2007: 	if (con->state != CEPH_CON_S_V2_HELLO) {
L2012: 	ceph_decode_8_safe(&p, end, entity_type, bad);
L2013: 	ret = ceph_decode_entity_addr(&p, end, &addr_for_me);
L2014: 	if (ret) {
L2019: 	dout("%s con %p entity_type %d addr_for_me %s\n", __func__, con,
L2020: 	     entity_type, ceph_pr_addr(&addr_for_me));
L2022: 	if (entity_type != con->peer_name.type) {
L2035: 	if (ceph_addr_is_blank(my_addr)) {
L2037: 		       sizeof(my_addr->in_addr));
L2038: 		ceph_addr_set_port(my_addr, 0);
L2039: 		dout("%s con %p set my addr %s, as seen by peer %s\n",
L2040: 		     __func__, con, ceph_pr_addr(my_addr),
L2041: 		     ceph_pr_addr(&con->peer_addr));
L2043: 		dout("%s con %p my addr already set %s\n",
L2044: 		     __func__, con, ceph_pr_addr(my_addr));
L2052: 	ret = prepare_auth_request(con);
```

#### Function: `static int process_auth_reply_more(struct ceph_connection *con,`

```c
L2129: static int process_auth_reply_more(struct ceph_connection *con,
L2130: 				   void *p, void *end)
L2135: 	if (con->state != CEPH_CON_S_V2_AUTH) {
L2140: 	ceph_decode_32_safe(&p, end, payload_len, bad);
L2141: 	ceph_decode_need(&p, end, payload_len, bad);
L2143: 	dout("%s con %p payload_len %d\n", __func__, con, payload_len);
L2145: 	reset_out_kvecs(con);
L2146: 	ret = prepare_auth_request_more(con, p, payload_len);
```

#### Function: `static int process_auth_done(struct ceph_connection *con, void *p, void *end)`

```c
L2166: static int process_auth_done(struct ceph_connection *con, void *p, void *end)
L2170: 	u8 *session_key = PTR_ALIGN(&session_key_buf[0], 16);
L2171: 	u8 *con_secret = PTR_ALIGN(&con_secret_buf[0], 16);
L2177: 	if (con->state != CEPH_CON_S_V2_AUTH) {
L2182: 	ceph_decode_64_safe(&p, end, global_id, bad);
L2183: 	ceph_decode_32_safe(&p, end, con->v2.con_mode, bad);
L2184: 	ceph_decode_32_safe(&p, end, payload_len, bad);
L2186: 	dout("%s con %p global_id %llu con_mode %d payload_len %d\n",
L2187: 	     __func__, con, global_id, con->v2.con_mode, payload_len);
L2189: 	mutex_unlock(&con->mutex);
L2190: 	session_key_len = 0;
L2191: 	con_secret_len = 0;
L2192: 	ret = con->ops->handle_auth_done(con, global_id, p, payload_len,
L2193: 					 session_key, &session_key_len,
L2194: 					 con_secret, &con_secret_len);
L2195: 	mutex_lock(&con->mutex);
L2196: 	if (con->state != CEPH_CON_S_V2_AUTH) {
L2203: 	dout("%s con %p handle_auth_done ret %d\n", __func__, con, ret);
L2204: 	if (ret)
L2207: 	ret = setup_crypto(con, session_key, session_key_len, con_secret,
L2209: 	if (ret)
L2212: 	reset_out_kvecs(con);
L2213: 	ret = prepare_auth_signature(con);
```

#### Function: `static int process_auth_signature(struct ceph_connection *con,`

```c
L2231: static int process_auth_signature(struct ceph_connection *con,
L2232: 				  void *p, void *end)
L2237: 	if (con->state != CEPH_CON_S_V2_AUTH_SIGNATURE) {
L2242: 	ret = hmac_sha256(con, con->v2.out_sign_kvecs,
L2243: 			  con->v2.out_sign_kvec_cnt, hmac);
L2244: 	if (ret)
L2247: 	ceph_decode_need(&p, end, SHA256_DIGEST_SIZE, bad);
L2248: 	if (crypto_memneq(p, hmac, SHA256_DIGEST_SIZE)) {
L2253: 	dout("%s con %p auth signature ok\n", __func__, con);
L2256: 	if (!con->v2.server_cookie) {
L2257: 		ret = prepare_client_ident(con);
L2265: 		ret = prepare_session_reconnect(con);
```

#### Function: `static int process_session_retry(struct ceph_connection *con,`

```c
L2416: static int process_session_retry(struct ceph_connection *con,
L2417: 				 void *p, void *end)
L2422: 	if (con->state != CEPH_CON_S_V2_SESSION_RECONNECT) {
L2427: 	ceph_decode_64_safe(&p, end, connect_seq, bad);
L2429: 	dout("%s con %p connect_seq %llu\n", __func__, con, connect_seq);
L2433: 	free_conn_bufs(con);
L2435: 	reset_out_kvecs(con);
L2436: 	ret = prepare_session_reconnect(con);
```

#### Function: `static int process_session_retry_global(struct ceph_connection *con,`

```c
L2449: static int process_session_retry_global(struct ceph_connection *con,
L2450: 					void *p, void *end)
L2455: 	if (con->state != CEPH_CON_S_V2_SESSION_RECONNECT) {
L2460: 	ceph_decode_64_safe(&p, end, global_seq, bad);
L2462: 	dout("%s con %p global_seq %llu\n", __func__, con, global_seq);
L2463: 	WARN_ON(global_seq <= con->v2.global_seq);
L2464: 	con->v2.global_seq = ceph_get_global_seq(con->msgr, global_seq);
L2466: 	free_conn_bufs(con);
L2468: 	reset_out_kvecs(con);
L2469: 	ret = prepare_session_reconnect(con);
```

#### Function: `static int process_session_reset(struct ceph_connection *con,`

```c
L2482: static int process_session_reset(struct ceph_connection *con,
L2483: 				 void *p, void *end)
L2488: 	if (con->state != CEPH_CON_S_V2_SESSION_RECONNECT) {
L2493: 	ceph_decode_8_safe(&p, end, full, bad);
L2494: 	if (!full) {
L2499: 	pr_info("%s%lld %s session reset\n", ENTITY_NAME(con->peer_name),
L2500: 		ceph_pr_addr(&con->peer_addr));
L2501: 	ceph_con_reset_session(con);
L2503: 	mutex_unlock(&con->mutex);
L2504: 	if (con->ops->peer_reset)
L2505: 		con->ops->peer_reset(con);
L2506: 	mutex_lock(&con->mutex);
L2507: 	if (con->state != CEPH_CON_S_V2_SESSION_RECONNECT) {
L2513: 	free_conn_bufs(con);
L2515: 	reset_out_kvecs(con);
L2516: 	ret = prepare_client_ident(con);
```

#### Function: `static int process_control(struct ceph_connection *con, void *p, void *end)`

```c
L2571: static int process_control(struct ceph_connection *con, void *p, void *end)
L2573: 	int tag = con->v2.in_desc.fd_tag;
L2576: 	dout("%s con %p tag %d len %d\n", __func__, con, tag, (int)(end - p));
L2578: 	switch (tag) {
L2580: 		ret = process_hello(con, p, end);
L2586: 		ret = process_auth_reply_more(con, p, end);
L2589: 		ret = process_auth_done(con, p, end);
L2592: 		ret = process_auth_signature(con, p, end);
L2604: 		ret = process_session_retry(con, p, end);
L2607: 		ret = process_session_retry_global(con, p, end);
L2610: 		ret = process_session_reset(con, p, end);
```

#### Function: `static int __handle_control(struct ceph_connection *con, void *p)`

```c
L2698: static int __handle_control(struct ceph_connection *con, void *p)
L2700: 	void *end = p + con->v2.in_desc.fd_lens[0];
L2704: 	if (con->v2.in_desc.fd_tag != FRAME_TAG_MESSAGE)
L2705: 		return process_control(con, p, end);
```

#### Function: `static int handle_preamble(struct ceph_connection *con)`

```c
L2738: static int handle_preamble(struct ceph_connection *con)
L2740: 	struct ceph_frame_desc *desc = &con->v2.in_desc;
L2743: 	if (con_secure(con)) {
L2744: 		ret = decrypt_preamble(con);
L2745: 		if (ret) {
L2752: 	ret = decode_preamble(con->v2.in_buf, desc);
L2753: 	if (ret) {
L2761: 	dout("%s con %p tag %d seg_cnt %d %d+%d+%d+%d\n", __func__,
L2762: 	     con, desc->fd_tag, desc->fd_seg_cnt, desc->fd_lens[0],
L2763: 	     desc->fd_lens[1], desc->fd_lens[2], desc->fd_lens[3]);
L2765: 	if (!con_secure(con))
L2766: 		return prepare_read_control(con);
L2768: 	if (desc->fd_lens[0] > CEPH_PREAMBLE_INLINE_LEN)
L2771: 	return __handle_control(con, CTRL_BODY(con->v2.in_buf));
```

#### Function: `static int handle_control(struct ceph_connection *con)`

```c
L2774: static int handle_control(struct ceph_connection *con)
L2776: 	int ctrl_len = con->v2.in_desc.fd_lens[0];
L2780: 	WARN_ON(con_secure(con));
L2782: 	ret = verify_control_crc(con);
L2783: 	if (ret) {
L2788: 	if (con->state == CEPH_CON_S_V2_AUTH) {
L2789: 		buf = alloc_conn_buf(con, ctrl_len);
L2790: 		if (!buf)
L2793: 		memcpy(buf, con->v2.in_kvecs[0].iov_base, ctrl_len);
L2794: 		return __handle_control(con, buf);
L2797: 	return __handle_control(con, con->v2.in_kvecs[0].iov_base);
```

#### Function: `static int handle_control_remainder(struct ceph_connection *con)`

```c
L2800: static int handle_control_remainder(struct ceph_connection *con)
L2804: 	WARN_ON(!con_secure(con));
L2806: 	ret = decrypt_control_remainder(con);
L2807: 	if (ret) {
L2813: 	return __handle_control(con, con->v2.in_kvecs[0].iov_base -
L2814: 				     CEPH_PREAMBLE_INLINE_LEN);
```

#### Function: `static int populate_in_iter(struct ceph_connection *con)`

```c
L2865: static int populate_in_iter(struct ceph_connection *con)
L2869: 	dout("%s con %p state %d in_state %d\n", __func__, con, con->state,
L2870: 	     con->v2.in_state);
L2873: 	if (con->state == CEPH_CON_S_V2_BANNER_PREFIX) {
L2875: 	} else if (con->state == CEPH_CON_S_V2_BANNER_PAYLOAD) {
L2876: 		ret = process_banner_payload(con);
L2877: 	} else if ((con->state >= CEPH_CON_S_V2_HELLO &&
L2878: 		    con->state <= CEPH_CON_S_V2_SESSION_RECONNECT) ||
L2879: 		   con->state == CEPH_CON_S_OPEN) {
L2880: 		switch (con->v2.in_state) {
L2882: 			ret = handle_preamble(con);
L2885: 			ret = handle_control(con);
L2888: 			ret = handle_control_remainder(con);
```

#### Function: `int ceph_con_v2_try_read(struct ceph_connection *con)`

```c
L2928: int ceph_con_v2_try_read(struct ceph_connection *con)
L2932: 	dout("%s con %p state %d need %zu\n", __func__, con, con->state,
L2933: 	     iov_iter_count(&con->v2.in_iter));
L2935: 	if (con->state == CEPH_CON_S_PREOPEN)
L2943: 	if (WARN_ON(!iov_iter_count(&con->v2.in_iter)))
L2947: 		ret = ceph_tcp_recv(con);
L2948: 		if (ret <= 0)
L2951: 		ret = populate_in_iter(con);
L2952: 		if (ret <= 0) {
```

#### Function: `static int padded_len(int len)`

```c
L377: static int padded_len(int len)
L379: 	return ALIGN(len, CEPH_GCM_BLOCK_LEN);
```

#### Function: `static int head_onwire_len(int ctrl_len, bool secure)`

```c
L388: static int head_onwire_len(int ctrl_len, bool secure)
L393: 	BUG_ON(ctrl_len < 0 || ctrl_len > CEPH_MSG_MAX_CONTROL_LEN);
L397: 		if (ctrl_len > CEPH_PREAMBLE_INLINE_LEN) {
L398: 			rem_len = ctrl_len - CEPH_PREAMBLE_INLINE_LEN;
L399: 			head_len += padded_len(rem_len) + CEPH_GCM_TAG_LEN;
L404: 			head_len += ctrl_len + CEPH_CRC_LEN;
L406: 	return head_len;
```

