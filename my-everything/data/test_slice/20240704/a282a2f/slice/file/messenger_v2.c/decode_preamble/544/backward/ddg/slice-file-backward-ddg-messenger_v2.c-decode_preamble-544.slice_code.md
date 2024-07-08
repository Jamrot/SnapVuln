### File: `code/code_old/net/ceph/messenger_v2.c`

#### Function: `static int handle_preamble(struct ceph_connection *con)`

```c
L2727: static int handle_preamble(struct ceph_connection *con)
L2729: 	struct ceph_frame_desc *desc = &con->v2.in_desc;
L2741: 	ret = decode_preamble(con->v2.in_buf, desc);
```

#### Function: `static int populate_in_iter(struct ceph_connection *con)`

```c
L2854: static int populate_in_iter(struct ceph_connection *con)
L2858: 	dout("%s con %p state %d in_state %d\n", __func__, con, con->state,
L2859: 	     con->v2.in_state);
L2862: 	if (con->state == CEPH_CON_S_V2_BANNER_PREFIX) {
L2864: 	} else if (con->state == CEPH_CON_S_V2_BANNER_PAYLOAD) {
L2866: 	} else if ((con->state >= CEPH_CON_S_V2_HELLO &&
L2867: 		    con->state <= CEPH_CON_S_V2_SESSION_RECONNECT) ||
L2868: 		   con->state == CEPH_CON_S_OPEN) {
L2871: 			ret = handle_preamble(con);
```

#### Function: `int ceph_con_v2_try_read(struct ceph_connection *con)`

```c
L2917: int ceph_con_v2_try_read(struct ceph_connection *con)
L2921: 	dout("%s con %p state %d need %zu\n", __func__, con, con->state,
L2922: 	     iov_iter_count(&con->v2.in_iter));
L2924: 	if (con->state == CEPH_CON_S_PREOPEN)
L2936: 		ret = ceph_tcp_recv(con);
L2940: 		ret = populate_in_iter(con);
```

#### Function: `static int decode_preamble(void *p, struct ceph_frame_desc *desc)`

```c
L495: static int decode_preamble(void *p, struct ceph_frame_desc *desc)
L497: 	void *crcp = p + CEPH_PREAMBLE_LEN - CEPH_CRC_LEN;
L501: 	crc = crc32c(0, p, crcp - p);
L509: 	memset(desc, 0, sizeof(*desc));
L511: 	desc->fd_tag = ceph_decode_8(&p);
L512: 	desc->fd_seg_cnt = ceph_decode_8(&p);
L513: 	if (desc->fd_seg_cnt < 1 ||
L514: 	    desc->fd_seg_cnt > CEPH_FRAME_MAX_SEGMENT_COUNT) {
L518: 	for (i = 0; i < desc->fd_seg_cnt; i++) {
L519: 		desc->fd_lens[i] = ceph_decode_32(&p);
L520: 		desc->fd_aligns[i] = ceph_decode_16(&p);
L527: 	if (!desc->fd_lens[desc->fd_seg_cnt - 1]) {
L532: 	if (desc->fd_lens[0] > CEPH_MSG_MAX_CONTROL_LEN) {
L536: 	if (desc->fd_lens[1] > CEPH_MSG_MAX_FRONT_LEN) {
L540: 	if (desc->fd_lens[2] > CEPH_MSG_MAX_MIDDLE_LEN) {
L544: 	if (desc->fd_lens[3] > CEPH_MSG_MAX_DATA_LEN) {
```

