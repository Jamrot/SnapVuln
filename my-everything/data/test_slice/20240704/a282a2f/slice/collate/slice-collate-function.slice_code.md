### File: `code/code_new/net/ceph/messenger_v2.c`

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

### File: `code/code_old/net/ceph/messenger_v2.c`

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
```

