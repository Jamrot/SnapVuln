### File: `code/code_new/net/ceph/messenger_v2.c`

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

