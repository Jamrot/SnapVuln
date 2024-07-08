### File: `code/code_new/net/ceph/messenger_v2.c`

#### Function: `static int decrypt_tail(struct ceph_connection *con)`

```c
L1042: static int decrypt_tail(struct ceph_connection *con)
L1044: 	struct sg_table enc_sgt = {};
L1045: 	struct sg_table sgt = {};
L1049: 	tail_len = tail_onwire_len(con->in_msg, true);
```

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
L1384: 	WARN_ON(con->v2.server_cookie);
L1385: 	WARN_ON(con->v2.connect_seq);
L1386: 	WARN_ON(con->v2.peer_global_seq);
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
L1437: 	WARN_ON(!con->v2.peer_global_seq);
L1439: 	dout("%s con %p my_addr %s/%u client_cookie 0x%llx server_cookie 0x%llx global_seq %llu connect_seq %llu in_seq %llu\n",
L1440: 	     __func__, con, ceph_pr_addr(my_addr), le32_to_cpu(my_addr->nonce),
L1441: 	     con->v2.client_cookie, con->v2.server_cookie, con->v2.global_seq,
L1442: 	     con->v2.connect_seq, con->in_seq);
L1444: 	ctrl_len = 1 + 4 + ceph_entity_addr_encoding_len(my_addr) + 5 * 8;
L1445: 	buf = alloc_conn_buf(con, head_onwire_len(ctrl_len, con_secure(con)));
```

#### Function: `static int prepare_message_secure(struct ceph_connection *con)`

```c
L1564: static int prepare_message_secure(struct ceph_connection *con)
L1566: 	void *zerop = page_address(ceph_zero_page);
L1567: 	struct sg_table enc_sgt = {};
L1568: 	struct sg_table sgt = {};
L1574: 	ret = prepare_head_secure_small(con, con->v2.out_buf,
L1575: 					sizeof(struct ceph_msg_header2));
L1576: 	if (ret)
L1579: 	tail_len = tail_onwire_len(con->out_msg, true);
```

#### Function: `static int prepare_message(struct ceph_connection *con)`

```c
L1628: static int prepare_message(struct ceph_connection *con)
L1630: 	int lens[] = {
L1631: 		sizeof(struct ceph_msg_header2),
L1632: 		front_len(con->out_msg),
L1633: 		middle_len(con->out_msg),
L1634: 		data_len(con->out_msg)
L1639: 	dout("%s con %p msg %p logical %d+%d+%d+%d\n", __func__, con,
L1640: 	     con->out_msg, lens[0], lens[1], lens[2], lens[3]);
L1642: 	if (con->in_seq > con->in_seq_acked) {
L1643: 		dout("%s con %p in_seq_acked %llu -> %llu\n", __func__, con,
L1644: 		     con->in_seq_acked, con->in_seq);
L1645: 		con->in_seq_acked = con->in_seq;
L1648: 	reset_out_kvecs(con);
L1649: 	init_frame_desc(&desc, FRAME_TAG_MESSAGE, lens, 4);
L1650: 	encode_preamble(&desc, con->v2.out_buf);
L1651: 	fill_header2(CTRL_BODY(con->v2.out_buf), &con->out_msg->hdr,
L1652: 		     con->in_seq_acked);
L1654: 	if (con_secure(con)) {
L1655: 		ret = prepare_message_secure(con);
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

#### Function: `static int prepare_read_tail_secure(struct ceph_connection *con)`

```c
L1884: static int prepare_read_tail_secure(struct ceph_connection *con)
L1890: 	tail_len = tail_onwire_len(con->in_msg, true);
```

#### Function: `static void prepare_skip_message(struct ceph_connection *con)`

```c
L1914: static void prepare_skip_message(struct ceph_connection *con)
L1916: 	struct ceph_frame_desc *desc = &con->v2.in_desc;
L1919: 	dout("%s con %p %d+%d+%d\n", __func__, con, desc->fd_lens[1],
L1920: 	     desc->fd_lens[2], desc->fd_lens[3]);
L1922: 	tail_len = __tail_onwire_len(desc->fd_lens[1], desc->fd_lens[2],
L1923: 				     desc->fd_lens[3], con_secure(con));
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
L2036: 		memcpy(&my_addr->in_addr, &addr_for_me.in_addr,
L2037: 		       sizeof(my_addr->in_addr));
L2038: 		ceph_addr_set_port(my_addr, 0);
L2039: 		dout("%s con %p set my addr %s, as seen by peer %s\n",
L2040: 		     __func__, con, ceph_pr_addr(my_addr),
L2041: 		     ceph_pr_addr(&con->peer_addr));
L2043: 		dout("%s con %p my addr already set %s\n",
L2044: 		     __func__, con, ceph_pr_addr(my_addr));
L2047: 	WARN_ON(ceph_addr_is_blank(my_addr) || ceph_addr_port(my_addr));
L2048: 	WARN_ON(my_addr->type != CEPH_ENTITY_ADDR_TYPE_ANY);
L2049: 	WARN_ON(!my_addr->nonce);
L2052: 	ret = prepare_auth_request(con);
```

#### Function: `static int process_auth_reply_more(struct ceph_connection *con,`

```c
L2129: static int process_auth_reply_more(struct ceph_connection *con,
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
L2208: 			   con_secret_len);
L2209: 	if (ret)
L2212: 	reset_out_kvecs(con);
L2213: 	ret = prepare_auth_signature(con);
```

#### Function: `static int process_auth_signature(struct ceph_connection *con,`

```c
L2231: static int process_auth_signature(struct ceph_connection *con,
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
L2422: 	if (con->state != CEPH_CON_S_V2_SESSION_RECONNECT) {
L2427: 	ceph_decode_64_safe(&p, end, connect_seq, bad);
L2429: 	dout("%s con %p connect_seq %llu\n", __func__, con, connect_seq);
L2430: 	WARN_ON(connect_seq <= con->v2.connect_seq);
L2431: 	con->v2.connect_seq = connect_seq + 1;
L2433: 	free_conn_bufs(con);
L2435: 	reset_out_kvecs(con);
L2436: 	ret = prepare_session_reconnect(con);
```

#### Function: `static int process_session_retry_global(struct ceph_connection *con,`

```c
L2449: static int process_session_retry_global(struct ceph_connection *con,
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
L2579: 	case FRAME_TAG_HELLO:
L2580: 		ret = process_hello(con, p, end);
L2585: 	case FRAME_TAG_AUTH_REPLY_MORE:
L2586: 		ret = process_auth_reply_more(con, p, end);
L2588: 	case FRAME_TAG_AUTH_DONE:
L2589: 		ret = process_auth_done(con, p, end);
L2591: 	case FRAME_TAG_AUTH_SIGNATURE:
L2592: 		ret = process_auth_signature(con, p, end);
L2603: 	case FRAME_TAG_SESSION_RETRY:
L2604: 		ret = process_session_retry(con, p, end);
L2606: 	case FRAME_TAG_SESSION_RETRY_GLOBAL:
L2607: 		ret = process_session_retry_global(con, p, end);
L2609: 	case FRAME_TAG_SESSION_RESET:
L2610: 		ret = process_session_reset(con, p, end);
```

#### Function: `static int __handle_control(struct ceph_connection *con, void *p)`

```c
L2698: static int __handle_control(struct ceph_connection *con, void *p)
L2700: 	void *end = p + con->v2.in_desc.fd_lens[0];
L2704: 	if (con->v2.in_desc.fd_tag != FRAME_TAG_MESSAGE)
L2705: 		return process_control(con, p, end);
L2707: 	ret = process_message_header(con, p, end);
L2708: 	if (ret < 0)
L2710: 	if (ret == 0) {
L2711: 		prepare_skip_message(con);
L2715: 	msg = con->in_msg;  /* set in process_message_header() */
L2716: 	if (front_len(msg)) {
L2717: 		WARN_ON(front_len(msg) > msg->front_alloc_len);
L2718: 		msg->front.iov_len = front_len(msg);
L2720: 		msg->front.iov_len = 0;
L2722: 	if (middle_len(msg)) {
L2723: 		WARN_ON(middle_len(msg) > msg->middle->alloc_len);
L2724: 		msg->middle->vec.iov_len = middle_len(msg);
L2725: 	} else if (msg->middle) {
L2726: 		msg->middle->vec.iov_len = 0;
L2729: 	if (!front_len(msg) && !middle_len(msg) && !data_len(msg))
L2732: 	if (con_secure(con))
L2733: 		return prepare_read_tail_secure(con);
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

#### Function: `static int handle_epilogue(struct ceph_connection *con)`

```c
L2817: static int handle_epilogue(struct ceph_connection *con)
L2822: 	if (con_secure(con)) {
L2823: 		ret = decrypt_tail(con);
```

#### Function: `static int populate_in_iter(struct ceph_connection *con)`

```c
L2865: static int populate_in_iter(struct ceph_connection *con)
L2869: 	dout("%s con %p state %d in_state %d\n", __func__, con, con->state,
L2870: 	     con->v2.in_state);
L2871: 	WARN_ON(iov_iter_count(&con->v2.in_iter));
L2873: 	if (con->state == CEPH_CON_S_V2_BANNER_PREFIX) {
L2875: 	} else if (con->state == CEPH_CON_S_V2_BANNER_PAYLOAD) {
L2876: 		ret = process_banner_payload(con);
L2877: 	} else if ((con->state >= CEPH_CON_S_V2_HELLO &&
L2878: 		    con->state <= CEPH_CON_S_V2_SESSION_RECONNECT) ||
L2879: 		   con->state == CEPH_CON_S_OPEN) {
L2880: 		switch (con->v2.in_state) {
L2881: 		case IN_S_HANDLE_PREAMBLE:
L2882: 			ret = handle_preamble(con);
L2884: 		case IN_S_HANDLE_CONTROL:
L2885: 			ret = handle_control(con);
L2887: 		case IN_S_HANDLE_CONTROL_REMAINDER:
L2888: 			ret = handle_control_remainder(con);
L2901: 		case IN_S_HANDLE_EPILOGUE:
L2902: 			ret = handle_epilogue(con);
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

#### Function: `static int populate_out_iter(struct ceph_connection *con)`

```c
L3068: static int populate_out_iter(struct ceph_connection *con)
L3072: 	dout("%s con %p state %d out_state %d\n", __func__, con, con->state,
L3073: 	     con->v2.out_state);
L3074: 	WARN_ON(iov_iter_count(&con->v2.out_iter));
L3076: 	if (con->state != CEPH_CON_S_OPEN) {
L3082: 	switch (con->v2.out_state) {
L3098: 	case OUT_S_FINISH_MESSAGE:
L3099: 		finish_message(con);
L3100: 		break;
L3101: 	case OUT_S_GET_NEXT:
L3102: 		break;
L3108: 	WARN_ON(con->v2.out_state != OUT_S_GET_NEXT);
L3109: 	if (ceph_con_flag_test_and_clear(con, CEPH_CON_F_KEEPALIVE_PENDING)) {
L3115: 	} else if (!list_empty(&con->out_queue)) {
L3116: 		ceph_con_get_out_msg(con);
L3117: 		ret = prepare_message(con);
```

#### Function: `int ceph_con_v2_try_write(struct ceph_connection *con)`

```c
L3146: int ceph_con_v2_try_write(struct ceph_connection *con)
L3150: 	dout("%s con %p state %d have %zu\n", __func__, con, con->state,
L3151: 	     iov_iter_count(&con->v2.out_iter));
L3154: 	if (con->state == CEPH_CON_S_PREOPEN) {
L3155: 		WARN_ON(con->peer_addr.type != CEPH_ENTITY_ADDR_TYPE_MSGR2);
L3162: 		con->v2.global_seq = ceph_get_global_seq(con->msgr, 0);
L3163: 		if (con->v2.server_cookie)
L3164: 			con->v2.connect_seq++;
L3166: 		ret = prepare_read_banner_prefix(con);
L3167: 		if (ret) {
L3173: 		reset_out_kvecs(con);
L3174: 		ret = prepare_banner(con);
L3175: 		if (ret) {
L3181: 		ret = ceph_tcp_connect(con);
L3182: 		if (ret) {
L3189: 	if (!iov_iter_count(&con->v2.out_iter)) {
L3190: 		ret = populate_out_iter(con);
L3191: 		if (ret <= 0) {
L3198: 	tcp_sock_set_cork(con->sock->sk, true);
L3200: 		ret = ceph_tcp_send(con);
L3201: 		if (ret <= 0)
L3204: 		ret = populate_out_iter(con);
L3205: 		if (ret <= 0) {
```

#### Function: `static int head_onwire_len(int ctrl_len, bool secure)`

```c
L388: static int head_onwire_len(int ctrl_len, bool secure)
L393: 	BUG_ON(ctrl_len < 0 || ctrl_len > CEPH_MSG_MAX_CONTROL_LEN);
```

#### Function: `static int __tail_onwire_len(int front_len, int middle_len, int data_len,`

```c
L410: static int __tail_onwire_len(int front_len, int middle_len, int data_len,
L413: 	BUG_ON(front_len < 0 || front_len > CEPH_MSG_MAX_FRONT_LEN ||
L414: 	       middle_len < 0 || middle_len > CEPH_MSG_MAX_MIDDLE_LEN ||
L415: 	       data_len < 0 || data_len > CEPH_MSG_MAX_DATA_LEN);
```

#### Function: `static int tail_onwire_len(const struct ceph_msg *msg, bool secure)`

```c
L428: static int tail_onwire_len(const struct ceph_msg *msg, bool secure)
L430: 	return __tail_onwire_len(front_len(msg), middle_len(msg),
L431: 				 data_len(msg), secure);
```

#### Function: `static int decode_preamble(void *p, struct ceph_frame_desc *desc)`

```c
L501: static int decode_preamble(void *p, struct ceph_frame_desc *desc)
L503: 	void *crcp = p + CEPH_PREAMBLE_LEN - CEPH_CRC_LEN;
L507: 	crc = crc32c(0, p, crcp - p);
L508: 	expected_crc = get_unaligned_le32(crcp);
L509: 	if (crc != expected_crc) {
L515: 	memset(desc, 0, sizeof(*desc));
L517: 	desc->fd_tag = ceph_decode_8(&p);
L518: 	desc->fd_seg_cnt = ceph_decode_8(&p);
L519: 	if (desc->fd_seg_cnt < 1 ||
L520: 	    desc->fd_seg_cnt > CEPH_FRAME_MAX_SEGMENT_COUNT) {
L524: 	for (i = 0; i < desc->fd_seg_cnt; i++) {
L525: 		desc->fd_lens[i] = ceph_decode_32(&p);
L526: 		desc->fd_aligns[i] = ceph_decode_16(&p);
L529: 	if (desc->fd_lens[0] < 0 ||
L530: 	    desc->fd_lens[0] > CEPH_MSG_MAX_CONTROL_LEN) {
```

