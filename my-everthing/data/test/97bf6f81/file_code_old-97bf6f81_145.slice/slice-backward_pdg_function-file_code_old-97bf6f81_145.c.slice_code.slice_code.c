int tipc_buf_append(struct sk_buff **headbuf, struct sk_buff **buf)
	struct sk_buff *head = *headbuf;
	struct sk_buff *frag = *buf;
	struct tipc_msg *msg;
	u32 fragid;
	if (!frag)
	msg = buf_msg(frag);
	fragid = msg_type(msg);
	if (fragid == FIRST_FRAGMENT) {
		if (unlikely(head))
		*buf = NULL;
