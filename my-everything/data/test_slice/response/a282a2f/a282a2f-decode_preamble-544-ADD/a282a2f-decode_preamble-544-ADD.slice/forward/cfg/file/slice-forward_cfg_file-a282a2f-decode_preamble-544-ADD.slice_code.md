### File: `code/code_new/net/ceph/messenger_v2.c`

#### Function: `static int decode_preamble(void *p, struct ceph_frame_desc *desc)`

```c
L501: static int decode_preamble(void *p, struct ceph_frame_desc *desc)
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

