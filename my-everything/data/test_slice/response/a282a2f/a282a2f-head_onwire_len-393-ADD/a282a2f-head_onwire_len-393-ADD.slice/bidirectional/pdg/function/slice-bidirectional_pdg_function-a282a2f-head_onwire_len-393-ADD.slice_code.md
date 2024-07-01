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

