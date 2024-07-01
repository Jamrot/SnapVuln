### File: `code/code_old/net/ceph/messenger_v2.c`

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
L518: 	for (i = 0; i < desc->fd_seg_cnt; i++) {
L519: 		desc->fd_lens[i] = ceph_decode_32(&p);
L520: 		desc->fd_aligns[i] = ceph_decode_16(&p);
L527: 	if (!desc->fd_lens[desc->fd_seg_cnt - 1]) {
L532: 	if (desc->fd_lens[0] > CEPH_MSG_MAX_CONTROL_LEN) {
L536: 	if (desc->fd_lens[1] > CEPH_MSG_MAX_FRONT_LEN) {
L540: 	if (desc->fd_lens[2] > CEPH_MSG_MAX_MIDDLE_LEN) {
L544: 	if (desc->fd_lens[3] > CEPH_MSG_MAX_DATA_LEN) {
```

### File: `code/code_new/net/ceph/messenger_v2.c`

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

#### Function: `static int __tail_onwire_len(int front_len, int middle_len, int data_len,`

```c
L410: static int __tail_onwire_len(int front_len, int middle_len, int data_len,
L413: 	BUG_ON(front_len < 0 || front_len > CEPH_MSG_MAX_FRONT_LEN ||
L414: 	       middle_len < 0 || middle_len > CEPH_MSG_MAX_MIDDLE_LEN ||
L415: 	       data_len < 0 || data_len > CEPH_MSG_MAX_DATA_LEN);
L417: 	if (!front_len && !middle_len && !data_len)
L418: 		return 0;
L420: 	if (!secure)
L421: 		return front_len + middle_len + data_len +
L422: 		       CEPH_EPILOGUE_PLAIN_LEN;
L424: 	return padded_len(front_len) + padded_len(middle_len) +
L425: 	       padded_len(data_len) + CEPH_EPILOGUE_SECURE_LEN;
```

#### Function: `static int decode_preamble(void *p, struct ceph_frame_desc *desc)`

```c
L501: static int decode_preamble(void *p, struct ceph_frame_desc *desc)
L529: 	if (desc->fd_lens[0] < 0 ||
L530: 	    desc->fd_lens[0] > CEPH_MSG_MAX_CONTROL_LEN) {
L531: 		pr_err("bad control segment length %d\n", desc->fd_lens[0]);
L532: 		return -EINVAL;
L534: 	if (desc->fd_lens[1] < 0 ||
L535: 	    desc->fd_lens[1] > CEPH_MSG_MAX_FRONT_LEN) {
L536: 		pr_err("bad front segment length %d\n", desc->fd_lens[1]);
L537: 		return -EINVAL;
L539: 	if (desc->fd_lens[2] < 0 ||
L540: 	    desc->fd_lens[2] > CEPH_MSG_MAX_MIDDLE_LEN) {
L541: 		pr_err("bad middle segment length %d\n", desc->fd_lens[2]);
L542: 		return -EINVAL;
L544: 	if (desc->fd_lens[3] < 0 ||
L545: 	    desc->fd_lens[3] > CEPH_MSG_MAX_DATA_LEN) {
L546: 		pr_err("bad data segment length %d\n", desc->fd_lens[3]);
L547: 		return -EINVAL;
L554: 	if (!desc->fd_lens[desc->fd_seg_cnt - 1]) {
L555: 		pr_err("last segment empty, segment count %d\n",
L556: 		       desc->fd_seg_cnt);
L557: 		return -EINVAL;
L560: 	return 0;
```

