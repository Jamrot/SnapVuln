static int tls_strp_copyin(read_descriptor_t *desc, struct sk_buff *in_skb,
	struct tls_strparser *strp = (struct tls_strparser *)desc->arg.data;
	struct sk_buff *skb;
	if (strp->msg_ready)
	skb = strp->anchor;
	if (!skb->len)
		skb_copy_decrypted(skb, in_skb);
		strp->mixed_decrypted |= !!skb_cmp_decrypted(skb, in_skb);
	if (IS_ENABLED(CONFIG_TLS_DEVICE) && strp->mixed_decrypted)
		ret = tls_strp_copyin_skb(strp, skb, in_skb, offset, in_len);
		ret = tls_strp_copyin_frag(strp, skb, in_skb, offset, in_len);
	if (strp->stm.full_len && strp->stm.full_len == skb->len) {
		strp->msg_ready = 1;
