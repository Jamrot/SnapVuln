### File: `code/code_new/net/ceph/messenger_v2.c`

#### Function: `static int decrypt_tail(struct ceph_connection *con)`

```c
L1042: static int decrypt_tail(struct ceph_connection *con)
L1044: 	struct sg_table enc_sgt = {};
L1045: 	struct sg_table sgt = {};
L1049: 	tail_len = tail_onwire_len(con->in_msg, true);
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

#### Function: `static int __handle_control(struct ceph_connection *con, void *p)`

```c
L2698: static int __handle_control(struct ceph_connection *con, void *p)
L2700: 	void *end = p + con->v2.in_desc.fd_lens[0];
L2704: 	if (con->v2.in_desc.fd_tag != FRAME_TAG_MESSAGE)
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
