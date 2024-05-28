int tipc_buf_append(struct sk_buff **headbuf, struct sk_buff **buf)
	struct sk_buff *head = *headbuf;
	struct sk_buff *frag = *buf;
	struct sk_buff *tail = NULL;
	if (!frag)
	msg = buf_msg(frag);
	fragid = msg_type(msg);
	frag->next = NULL;
	skb_pull(frag, msg_hdr_sz(msg));
	if (fragid == FIRST_FRAGMENT) {
		if (unlikely(head))
		*buf = NULL;
