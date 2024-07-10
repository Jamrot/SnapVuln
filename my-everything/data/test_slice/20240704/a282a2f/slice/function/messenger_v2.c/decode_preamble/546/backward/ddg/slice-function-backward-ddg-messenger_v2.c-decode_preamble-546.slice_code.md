### File: `code/code_new/net/ceph/messenger_v2.c`

#### Function: `static int decode_preamble(void *p, struct ceph_frame_desc *desc)`

```c
L501: static int decode_preamble(void *p, struct ceph_frame_desc *desc)
L503: 	void *crcp = p + CEPH_PREAMBLE_LEN - CEPH_CRC_LEN;
L507: 	crc = crc32c(0, p, crcp - p);
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
L534: 	if (desc->fd_lens[1] < 0 ||
L535: 	    desc->fd_lens[1] > CEPH_MSG_MAX_FRONT_LEN) {
L539: 	if (desc->fd_lens[2] < 0 ||
L540: 	    desc->fd_lens[2] > CEPH_MSG_MAX_MIDDLE_LEN) {
L544: 	if (desc->fd_lens[3] < 0 ||
L545: 	    desc->fd_lens[3] > CEPH_MSG_MAX_DATA_LEN) {
L546: 		pr_err("bad data segment length %d\n", desc->fd_lens[3]);
```

