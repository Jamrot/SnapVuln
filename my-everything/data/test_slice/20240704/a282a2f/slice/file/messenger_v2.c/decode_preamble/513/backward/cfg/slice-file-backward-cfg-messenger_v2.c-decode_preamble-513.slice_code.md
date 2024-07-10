### File: `code/code_old/net/ceph/messenger_v2.c`

#### Function: `static int handle_preamble(struct ceph_connection *con)`

```c
L2727: static int handle_preamble(struct ceph_connection *con)
L2729: 	struct ceph_frame_desc *desc = &con->v2.in_desc;
L2732: 	if (con_secure(con)) {
L2733: 		ret = decrypt_preamble(con);
L2734: 		if (ret) {
L2741: 	ret = decode_preamble(con->v2.in_buf, desc);
```

#### Function: `static int populate_in_iter(struct ceph_connection *con)`

```c
L2854: static int populate_in_iter(struct ceph_connection *con)
L2858: 	dout("%s con %p state %d in_state %d\n", __func__, con, con->state,
L2859: 	     con->v2.in_state);
L2860: 	WARN_ON(iov_iter_count(&con->v2.in_iter));
L2862: 	if (con->state == CEPH_CON_S_V2_BANNER_PREFIX) {
L2864: 	} else if (con->state == CEPH_CON_S_V2_BANNER_PAYLOAD) {
L2866: 	} else if ((con->state >= CEPH_CON_S_V2_HELLO &&
L2867: 		    con->state <= CEPH_CON_S_V2_SESSION_RECONNECT) ||
L2868: 		   con->state == CEPH_CON_S_OPEN) {
L2869: 		switch (con->v2.in_state) {
L2870: 		case IN_S_HANDLE_PREAMBLE:
L2871: 			ret = handle_preamble(con);
```

#### Function: `int ceph_con_v2_try_read(struct ceph_connection *con)`

```c
L2917: int ceph_con_v2_try_read(struct ceph_connection *con)
L2921: 	dout("%s con %p state %d need %zu\n", __func__, con, con->state,
L2922: 	     iov_iter_count(&con->v2.in_iter));
L2924: 	if (con->state == CEPH_CON_S_PREOPEN)
L2932: 	if (WARN_ON(!iov_iter_count(&con->v2.in_iter)))
L2936: 		ret = ceph_tcp_recv(con);
L2937: 		if (ret <= 0)
L2940: 		ret = populate_in_iter(con);
L2941: 		if (ret <= 0) {
```

#### Function: `static int decode_preamble(void *p, struct ceph_frame_desc *desc)`

```c
L495: static int decode_preamble(void *p, struct ceph_frame_desc *desc)
L497: 	void *crcp = p + CEPH_PREAMBLE_LEN - CEPH_CRC_LEN;
L501: 	crc = crc32c(0, p, crcp - p);
L502: 	expected_crc = get_unaligned_le32(crcp);
L503: 	if (crc != expected_crc) {
L509: 	memset(desc, 0, sizeof(*desc));
L511: 	desc->fd_tag = ceph_decode_8(&p);
L512: 	desc->fd_seg_cnt = ceph_decode_8(&p);
L513: 	if (desc->fd_seg_cnt < 1 ||
L514: 	    desc->fd_seg_cnt > CEPH_FRAME_MAX_SEGMENT_COUNT) {
```

