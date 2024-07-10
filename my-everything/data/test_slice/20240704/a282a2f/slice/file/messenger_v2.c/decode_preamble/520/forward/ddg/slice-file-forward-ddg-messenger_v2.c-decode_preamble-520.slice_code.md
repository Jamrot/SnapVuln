### File: `code/code_old/net/ceph/messenger_v2.c`

#### Function: `static int decode_preamble(void *p, struct ceph_frame_desc *desc)`

```c
L519: 		desc->fd_lens[i] = ceph_decode_32(&p);
L520: 		desc->fd_aligns[i] = ceph_decode_16(&p);
L527: 	if (!desc->fd_lens[desc->fd_seg_cnt - 1]) {
L532: 	if (desc->fd_lens[0] > CEPH_MSG_MAX_CONTROL_LEN) {
L533: 		pr_err("control segment too big %d\n", desc->fd_lens[0]);
L536: 	if (desc->fd_lens[1] > CEPH_MSG_MAX_FRONT_LEN) {
L537: 		pr_err("front segment too big %d\n", desc->fd_lens[1]);
L540: 	if (desc->fd_lens[2] > CEPH_MSG_MAX_MIDDLE_LEN) {
L541: 		pr_err("middle segment too big %d\n", desc->fd_lens[2]);
L544: 	if (desc->fd_lens[3] > CEPH_MSG_MAX_DATA_LEN) {
L545: 		pr_err("data segment too big %d\n", desc->fd_lens[3]);
```

