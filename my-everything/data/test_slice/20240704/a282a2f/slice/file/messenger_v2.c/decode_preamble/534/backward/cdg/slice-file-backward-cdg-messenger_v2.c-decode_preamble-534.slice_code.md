### File: `code/code_new/net/ceph/messenger_v2.c`

#### Function: `static int decode_preamble(void *p, struct ceph_frame_desc *desc)`

```c
L509: 	if (crc != expected_crc) {
L519: 	if (desc->fd_seg_cnt < 1 ||
L529: 	if (desc->fd_lens[0] < 0 ||
L534: 	if (desc->fd_lens[1] < 0 ||
```

