### File: `code/code_new/net/ceph/messenger_v2.c`

#### Function: `static int handle_preamble(struct ceph_connection *con)`

```c
L2738: static int handle_preamble(struct ceph_connection *con)
L2740: 	struct ceph_frame_desc *desc = &con->v2.in_desc;
L2743: 	if (con_secure(con)) {
L2744: 		ret = decrypt_preamble(con);
L2745: 		if (ret) {
L2752: 	ret = decode_preamble(con->v2.in_buf, desc);
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

