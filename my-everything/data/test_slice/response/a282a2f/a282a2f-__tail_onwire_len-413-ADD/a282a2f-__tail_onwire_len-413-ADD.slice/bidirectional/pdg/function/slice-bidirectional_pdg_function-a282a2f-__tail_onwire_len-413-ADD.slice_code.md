### File: `code/code_new/net/ceph/messenger_v2.c`

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

