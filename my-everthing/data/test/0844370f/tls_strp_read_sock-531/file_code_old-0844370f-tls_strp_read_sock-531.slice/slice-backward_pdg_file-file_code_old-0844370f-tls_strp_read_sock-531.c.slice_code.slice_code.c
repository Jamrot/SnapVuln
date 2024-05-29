static int tls_strp_read_sock(struct tls_strparser *strp)
	int sz, inq;
	inq = tcp_inq(strp->sk);
	if (inq < 1)
	if (unlikely(strp->copy_mode))
	if (inq < strp->stm.full_len)
	if (!strp->stm.full_len) {
		tls_strp_load_anchor_with_queue(strp, inq);
		sz = tls_rx_msg_size(strp, strp->anchor);
		if (sz < 0) {
		strp->stm.full_len = sz;
		if (!strp->stm.full_len || inq < strp->stm.full_len)
	if (!tls_strp_check_queue_ok(strp))
	strp->msg_ready = 1;
void tls_strp_check_rcv(struct tls_strparser *strp)
	if (unlikely(strp->stopped) || strp->msg_ready)
	if (tls_strp_read_sock(strp) == -ENOMEM)
void tls_strp_data_ready(struct tls_strparser *strp)
	if (sock_owned_by_user_nocheck(strp->sk)) {
	tls_strp_check_rcv(strp);
static void tls_strp_work(struct work_struct *w)
	lock_sock(strp->sk);
	tls_strp_check_rcv(strp);
void tls_strp_msg_done(struct tls_strparser *strp)
	WARN_ON(!strp->stm.full_len);
	if (likely(!strp->copy_mode))
		tcp_read_done(strp->sk, strp->stm.full_len);
		tls_strp_flush_anchor_copy(strp);
	strp->msg_ready = 0;
	memset(&strp->stm, 0, sizeof(strp->stm));
	tls_strp_check_rcv(strp);
