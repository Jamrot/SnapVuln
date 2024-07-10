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
L536: 	if (desc->fd_lens[1] > CEPH_MSG_MAX_FRONT_LEN) {
L537: 		pr_err("front segment too big %d\n", desc->fd_lens[1]);
```

