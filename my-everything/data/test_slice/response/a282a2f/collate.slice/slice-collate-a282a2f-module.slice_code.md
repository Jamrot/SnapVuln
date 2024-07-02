### File: `code/code_old/net/ceph/snapshot.c`

#### Function: `void ceph_put_snap_context(struct ceph_snap_context *sc)`

```c
L54: void ceph_put_snap_context(struct ceph_snap_context *sc)
L56: 	if (!sc)
L57: 		return;
L58: 	if (refcount_dec_and_test(&sc->nref)) {
L60: 		kfree(sc);
```

### File: `code/code_old/net/ceph/osdmap.c`

#### Function: `void ceph_oloc_destroy(struct ceph_object_locator *oloc)`

```c
L2131: void ceph_oloc_destroy(struct ceph_object_locator *oloc)
L2133: 	ceph_put_string(oloc->pool_ns);
```

#### Function: `void ceph_oid_destroy(struct ceph_object_id *oid)`

```c
L2225: void ceph_oid_destroy(struct ceph_object_id *oid)
L2227: 	if (oid->name != oid->inline_name)
L2228: 		kfree(oid->name);
```

### File: `code/code_old/net/ceph/messenger.c`

#### Function: `void ceph_msg_put(struct ceph_msg *msg)`

```c
L2191: void ceph_msg_put(struct ceph_msg *msg)
L2193: 	dout("%s %p (was %d)\n", __func__, msg,
L2194: 	     kref_read(&msg->kref));
L2195: 	kref_put(&msg->kref, ceph_msg_release);
```

#### Function: `static void ceph_con_reset_protocol(struct ceph_connection *con)`

```c
L508: static void ceph_con_reset_protocol(struct ceph_connection *con)
L519: 		WARN_ON(con->out_msg->con != con);
L520: 		ceph_msg_put(con->out_msg);
L521: 		con->out_msg = NULL;
L523: 	if (con->bounce_page) {
L524: 		__free_page(con->bounce_page);
L525: 		con->bounce_page = NULL;
L528: 	if (ceph_msgr2(from_msgr(con->msgr)))
L529: 		ceph_con_v2_reset_protocol(con);
L531: 		ceph_con_v1_reset_protocol(con);
```

### File: `code/code_old/net/ceph/messenger_v2.c`

#### Function: `static void free_conn_bufs(struct ceph_connection *con)`

```c
L318: static void free_conn_bufs(struct ceph_connection *con)
L320: 	while (con->v2.conn_buf_cnt)
L321: 		kvfree(con->v2.conn_bufs[--con->v2.conn_buf_cnt]);
```

#### Function: `static void clear_in_sign_kvecs(struct ceph_connection *con)`

```c
L333: static void clear_in_sign_kvecs(struct ceph_connection *con)
L335: 	con->v2.in_sign_kvec_cnt = 0;
```

#### Function: `static void clear_out_sign_kvecs(struct ceph_connection *con)`

```c
L347: static void clear_out_sign_kvecs(struct ceph_connection *con)
L349: 	con->v2.out_sign_kvec_cnt = 0;
```

#### Function: `void ceph_con_v2_reset_protocol(struct ceph_connection *con)`

```c
L3529: void ceph_con_v2_reset_protocol(struct ceph_connection *con)
L3531: 	iov_iter_truncate(&con->v2.in_iter, 0);
L3532: 	iov_iter_truncate(&con->v2.out_iter, 0);
L3533: 	con->v2.out_zero = 0;
L3535: 	clear_in_sign_kvecs(con);
L3536: 	clear_out_sign_kvecs(con);
L3537: 	free_conn_bufs(con);
L3539: 	if (con->v2.in_enc_pages) {
L3540: 		WARN_ON(!con->v2.in_enc_page_cnt);
L3541: 		ceph_release_page_vector(con->v2.in_enc_pages,
L3542: 					 con->v2.in_enc_page_cnt);
L3543: 		con->v2.in_enc_pages = NULL;
L3544: 		con->v2.in_enc_page_cnt = 0;
L3546: 	if (con->v2.out_enc_pages) {
L3547: 		WARN_ON(!con->v2.out_enc_page_cnt);
L3548: 		ceph_release_page_vector(con->v2.out_enc_pages,
L3549: 					 con->v2.out_enc_page_cnt);
L3550: 		con->v2.out_enc_pages = NULL;
L3551: 		con->v2.out_enc_page_cnt = 0;
L3554: 	con->v2.con_mode = CEPH_CON_MODE_UNKNOWN;
L3555: 	memzero_explicit(&con->v2.in_gcm_nonce, CEPH_GCM_IV_LEN);
L3556: 	memzero_explicit(&con->v2.out_gcm_nonce, CEPH_GCM_IV_LEN);
L3558: 	if (con->v2.hmac_tfm) {
L3559: 		crypto_free_shash(con->v2.hmac_tfm);
L3560: 		con->v2.hmac_tfm = NULL;
L3562: 	if (con->v2.gcm_req) {
L3563: 		aead_request_free(con->v2.gcm_req);
L3564: 		con->v2.gcm_req = NULL;
L3566: 	if (con->v2.gcm_tfm) {
L3567: 		crypto_free_aead(con->v2.gcm_tfm);
L3568: 		con->v2.gcm_tfm = NULL;
```

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

### File: `code/code_old/net/ceph/osd_client.c`

#### Function: `static void osd_req_op_data_release(struct ceph_osd_request *osd_req,`

```c
L394: static void osd_req_op_data_release(struct ceph_osd_request *osd_req,
L395: 			unsigned int which)
L399: 	BUG_ON(which >= osd_req->r_num_ops);
L400: 	op = &osd_req->r_ops[which];
L402: 	switch (op->op) {
L403: 	case CEPH_OSD_OP_READ:
L404: 	case CEPH_OSD_OP_SPARSE_READ:
L405: 	case CEPH_OSD_OP_WRITE:
L406: 	case CEPH_OSD_OP_WRITEFULL:
L407: 		kfree(op->extent.sparse_ext);
L408: 		ceph_osd_data_release(&op->extent.osd_data);
L410: 	case CEPH_OSD_OP_CALL:
L411: 		ceph_osd_data_release(&op->cls.request_info);
L412: 		ceph_osd_data_release(&op->cls.request_data);
L413: 		ceph_osd_data_release(&op->cls.response_data);
L415: 	case CEPH_OSD_OP_SETXATTR:
L416: 	case CEPH_OSD_OP_CMPXATTR:
L417: 		ceph_osd_data_release(&op->xattr.osd_data);
L419: 	case CEPH_OSD_OP_STAT:
L420: 		ceph_osd_data_release(&op->raw_data_in);
L422: 	case CEPH_OSD_OP_NOTIFY_ACK:
L423: 		ceph_osd_data_release(&op->notify_ack.request_data);
L425: 	case CEPH_OSD_OP_NOTIFY:
L426: 		ceph_osd_data_release(&op->notify.request_data);
L427: 		ceph_osd_data_release(&op->notify.response_data);
L429: 	case CEPH_OSD_OP_LIST_WATCHERS:
L430: 		ceph_osd_data_release(&op->list_watchers.response_data);
L432: 	case CEPH_OSD_OP_COPY_FROM2:
L433: 		ceph_osd_data_release(&op->copy_from.osd_data);
```

#### Function: `static void target_destroy(struct ceph_osd_request_target *t)`

```c
L487: static void target_destroy(struct ceph_osd_request_target *t)
L489: 	ceph_oid_destroy(&t->base_oid);
L490: 	ceph_oloc_destroy(&t->base_oloc);
L491: 	ceph_oid_destroy(&t->target_oid);
L492: 	ceph_oloc_destroy(&t->target_oloc);
```

#### Function: `static void ceph_osdc_release_request(struct kref *kref)`

```c
L506: static void ceph_osdc_release_request(struct kref *kref)
L519: 		ceph_msg_put(req->r_reply);
L521: 	for (which = 0; which < req->r_num_ops; which++)
L522: 		osd_req_op_data_release(req, which);
L524: 	target_destroy(&req->r_t);
L525: 	ceph_put_snap_context(req->r_snapc);
L527: 	if (req->r_mempool)
L528: 		mempool_free(req, req->r_osdc->req_mempool);
L529: 	else if (req->r_num_ops <= CEPH_OSD_SLAB_OPS)
L530: 		kmem_cache_free(ceph_osd_request_cache, req);
L532: 		kfree(req);
```

### File: `code/code_old/net/ceph/ceph_common.c`

#### Function: `int ceph_parse_param(struct fs_parameter *param, struct ceph_options *opt,`

```c
L519: 		case Opt_ms_mode_prefer_secure:
```

### File: `code/code_old/net/ceph/messenger_v1.c`

#### Function: `static void con_out_kvec_add(struct ceph_connection *con,`

```c
L119: static void con_out_kvec_add(struct ceph_connection *con,
L120: 				size_t size, void *data)
L122: 	int index = con->v1.out_kvec_left;
L124: 	BUG_ON(con->v1.out_skip);
L125: 	BUG_ON(index >= ARRAY_SIZE(con->v1.out_kvec));
L127: 	con->v1.out_kvec[index].iov_len = size;
L128: 	con->v1.out_kvec[index].iov_base = data;
L129: 	con->v1.out_kvec_left++;
L130: 	con->v1.out_kvec_bytes += size;
```

#### Function: `static size_t sizeof_footer(struct ceph_connection *con)`

```c
L153: static size_t sizeof_footer(struct ceph_connection *con)
L155: 	return (con->peer_features & CEPH_FEATURE_MSG_AUTH) ?
```

#### Function: `void ceph_con_v1_reset_protocol(struct ceph_connection *con)`

```c
L1621: void ceph_con_v1_reset_protocol(struct ceph_connection *con)
L1623: 	con->v1.out_skip = 0;
```

#### Function: `static void prepare_write_message_footer(struct ceph_connection *con)`

```c
L172: static void prepare_write_message_footer(struct ceph_connection *con)
L174: 	struct ceph_msg *m = con->out_msg;
L176: 	m->footer.flags |= CEPH_MSG_FOOTER_COMPLETE;
L178: 	dout("prepare_write_message_footer %p\n", con);
L179: 	con_out_kvec_add(con, sizeof_footer(con), &m->footer);
L180: 	if (con->peer_features & CEPH_FEATURE_MSG_AUTH) {
L181: 		if (con->ops->sign_message)
L182: 			con->ops->sign_message(m);
L184: 			m->footer.sig = 0;
L186: 		m->old_footer.flags = m->footer.flags;
L188: 	con->v1.out_more = m->more_to_follow;
L189: 	con->v1.out_msg_done = true;
```

#### Function: `static int write_partial_message_data(struct ceph_connection *con)`

```c
L519: 	prepare_write_message_footer(con);
```

### File: `code/code_old/net/ceph/mon_client.c`

#### Function: `int ceph_monc_wait_osdmap(struct ceph_mon_client *monc, u32 epoch,`

```c
L496: int ceph_monc_wait_osdmap(struct ceph_mon_client *monc, u32 epoch,
L519: 	return 0;
```

### File: `code/code_old/net/ceph/crush/mapper.c`

#### Function: `static int bucket_perm_choose(const struct crush_bucket *bucket,`

```c
L100: 		for (i = 1; i < bucket->size; i++)
L101: 			work->perm[i] = i;
L102: 		work->perm[work->perm[0]] = 0;
L103: 		work->perm_n = 1;
L107: 	for (i = 0; i < work->perm_n; i++)
L109: 	while (work->perm_n <= pr) {
L110: 		unsigned int p = work->perm_n;
L112: 		if (p < bucket->size - 1) {
L113: 			i = crush_hash32_3(bucket->hash, x, bucket->id, p) %
L114: 				(bucket->size - p);
L115: 			if (i) {
L116: 				unsigned int t = work->perm[p + i];
L117: 				work->perm[p + i] = work->perm[p];
L118: 				work->perm[p] = t;
L122: 		work->perm_n++;
L124: 	for (i = 0; i < bucket->size; i++)
L127: 	s = work->perm[pr];
L131: 	return bucket->items[s];
```

#### Function: `static int bucket_uniform_choose(const struct crush_bucket_uniform *bucket,`

```c
L135: static int bucket_uniform_choose(const struct crush_bucket_uniform *bucket,
L136: 				 struct crush_work_bucket *work, int x, int r)
L138: 	return bucket_perm_choose(&bucket->h, work, x, r);
```

#### Function: `static int bucket_list_choose(const struct crush_bucket_list *bucket,`

```c
L142: static int bucket_list_choose(const struct crush_bucket_list *bucket,
L143: 			      int x, int r)
L147: 	for (i = bucket->h.size-1; i >= 0; i--) {
L148: 		__u64 w = crush_hash32_4(bucket->h.hash, x, bucket->h.items[i],
L149: 					 r, bucket->h.id);
L150: 		w &= 0xffff;
L155: 		w *= bucket->sum_weights[i];
L156: 		w = w >> 16;
L158: 		if (w < bucket->item_weights[i]) {
L159: 			return bucket->h.items[i];
L164: 	return bucket->h.items[0];
```

#### Function: `static int height(int n)`

```c
L169: static int height(int n)
L171: 	int h = 0;
L172: 	while ((n & 1) == 0) {
L173: 		h++;
L174: 		n = n >> 1;
L176: 	return h;
```

#### Function: `static int left(int x)`

```c
L179: static int left(int x)
L181: 	int h = height(x);
L182: 	return x - (1 << (h-1));
```

#### Function: `static int right(int x)`

```c
L185: static int right(int x)
L187: 	int h = height(x);
L188: 	return x + (1 << (h-1));
```

#### Function: `static int terminal(int x)`

```c
L191: static int terminal(int x)
L193: 	return x & 1;
```

#### Function: `static int bucket_tree_choose(const struct crush_bucket_tree *bucket,`

```c
L196: static int bucket_tree_choose(const struct crush_bucket_tree *bucket,
L197: 			      int x, int r)
L204: 	n = bucket->num_nodes >> 1;
L206: 	while (!terminal(n)) {
L209: 		w = bucket->node_weights[n];
L210: 		t = (__u64)crush_hash32_4(bucket->h.hash, x, n, r,
L211: 					  bucket->h.id) * (__u64)w;
L212: 		t = t >> 32;
L215: 		l = left(n);
L216: 		if (t < bucket->node_weights[l])
L217: 			n = l;
L219: 			n = right(n);
L222: 	return bucket->h.items[n >> 1];
```

#### Function: `static int bucket_straw_choose(const struct crush_bucket_straw *bucket,`

```c
L228: static int bucket_straw_choose(const struct crush_bucket_straw *bucket,
L229: 			       int x, int r)
L232: 	int high = 0;
L233: 	__u64 high_draw = 0;
L236: 	for (i = 0; i < bucket->h.size; i++) {
L237: 		draw = crush_hash32_3(bucket->h.hash, x, bucket->h.items[i], r);
L238: 		draw &= 0xffff;
L239: 		draw *= bucket->straws[i];
L240: 		if (i == 0 || draw > high_draw) {
L241: 			high = i;
L242: 			high_draw = draw;
L245: 	return bucket->h.items[high];
```

#### Function: `static __u64 crush_ln(unsigned int xin)`

```c
L249: static __u64 crush_ln(unsigned int xin)
L251: 	unsigned int x = xin;
L255: 	x++;
L258: 	iexpon = 15;
L264: 	if (!(x & 0x18000)) {
L265: 		int bits = __builtin_clz(x & 0x1FFFF) - 16;
L266: 		x <<= bits;
L267: 		iexpon = 15 - bits;
L270: 	index1 = (x >> 8) << 1;
L272: 	RH = __RH_LH_tbl[index1 - 256];
L274: 	LH = __RH_LH_tbl[index1 + 1 - 256];
L277: 	xl64 = (__s64)x * RH;
L278: 	xl64 >>= 48;
L280: 	result = iexpon;
L281: 	result <<= (12 + 32);
L283: 	index2 = xl64 & 0xff;
L285: 	LL = __LL_tbl[index2];
L287: 	LH = LH + LL;
L289: 	LH >>= (48 - 12 - 32);
L290: 	result += LH;
L292: 	return result;
```

#### Function: `static __u32 *get_choose_arg_weights(const struct crush_bucket_straw2 *bucket,`

```c
L305: static __u32 *get_choose_arg_weights(const struct crush_bucket_straw2 *bucket,
L306: 				     const struct crush_choose_arg *arg,
L307: 				     int position)
L309: 	if (!arg || !arg->weight_set)
L310: 		return bucket->item_weights;
L312: 	if (position >= arg->weight_set_size)
L313: 		position = arg->weight_set_size - 1;
L314: 	return arg->weight_set[position].weights;
```

#### Function: `static __s32 *get_choose_arg_ids(const struct crush_bucket_straw2 *bucket,`

```c
L317: static __s32 *get_choose_arg_ids(const struct crush_bucket_straw2 *bucket,
L318: 				 const struct crush_choose_arg *arg)
L320: 	if (!arg || !arg->ids)
L321: 		return bucket->h.items;
L323: 	return arg->ids;
```

#### Function: `static int bucket_straw2_choose(const struct crush_bucket_straw2 *bucket,`

```c
L326: static int bucket_straw2_choose(const struct crush_bucket_straw2 *bucket,
L327: 				int x, int r,
L328: 				const struct crush_choose_arg *arg,
L329: 				int position)
L331: 	unsigned int i, high = 0;
L333: 	__s64 ln, draw, high_draw = 0;
L334: 	__u32 *weights = get_choose_arg_weights(bucket, arg, position);
L335: 	__s32 *ids = get_choose_arg_ids(bucket, arg);
L337: 	for (i = 0; i < bucket->h.size; i++) {
L339: 		if (weights[i]) {
L340: 			u = crush_hash32_3(bucket->h.hash, x, ids[i], r);
L341: 			u &= 0xffff;
L353: 			ln = crush_ln(u) - 0x1000000000000ll;
L361: 			draw = div64_s64(ln, weights[i]);
L363: 			draw = S64_MIN;
L366: 		if (i == 0 || draw > high_draw) {
L367: 			high = i;
L368: 			high_draw = draw;
L372: 	return bucket->h.items[high];
```

#### Function: `static int crush_bucket_choose(const struct crush_bucket *in,`

```c
L376: static int crush_bucket_choose(const struct crush_bucket *in,
L377: 			       struct crush_work_bucket *work,
L378: 			       int x, int r,
L379: 			       const struct crush_choose_arg *arg,
L380: 			       int position)
L383: 	BUG_ON(in->size == 0);
L384: 	switch (in->alg) {
L385: 	case CRUSH_BUCKET_UNIFORM:
L386: 		return bucket_uniform_choose(
L387: 			(const struct crush_bucket_uniform *)in,
L388: 			work, x, r);
L389: 	case CRUSH_BUCKET_LIST:
L390: 		return bucket_list_choose((const struct crush_bucket_list *)in,
L391: 					  x, r);
L392: 	case CRUSH_BUCKET_TREE:
L393: 		return bucket_tree_choose((const struct crush_bucket_tree *)in,
L394: 					  x, r);
L395: 	case CRUSH_BUCKET_STRAW:
L396: 		return bucket_straw_choose(
L397: 			(const struct crush_bucket_straw *)in,
L398: 			x, r);
L399: 	case CRUSH_BUCKET_STRAW2:
L400: 		return bucket_straw2_choose(
L401: 			(const struct crush_bucket_straw2 *)in,
L402: 			x, r, arg, position);
L405: 		return in->items[0];
```

#### Function: `static int is_out(const struct crush_map *map,`

```c
L413: static int is_out(const struct crush_map *map,
L414: 		  const __u32 *weight, int weight_max,
L415: 		  int item, int x)
L417: 	if (item >= weight_max)
L418: 		return 1;
L419: 	if (weight[item] >= 0x10000)
L420: 		return 0;
L421: 	if (weight[item] == 0)
L422: 		return 1;
L423: 	if ((crush_hash32_2(CRUSH_HASH_RJENKINS1, x, item) & 0xffff)
L424: 	    < weight[item])
L425: 		return 0;
L426: 	return 1;
```

#### Function: `static int crush_choose_firstn(const struct crush_map *map,`

```c
L449: static int crush_choose_firstn(const struct crush_map *map,
L450: 			       struct crush_work *work,
L451: 			       const struct crush_bucket *bucket,
L452: 			       const __u32 *weight, int weight_max,
L453: 			       int x, int numrep, int type,
L454: 			       int *out, int outpos,
L455: 			       int out_size,
L456: 			       unsigned int tries,
L457: 			       unsigned int recurse_tries,
L458: 			       unsigned int local_retries,
L459: 			       unsigned int local_fallback_retries,
L460: 			       int recurse_to_leaf,
L461: 			       unsigned int vary_r,
L462: 			       unsigned int stable,
L463: 			       int *out2,
L464: 			       int parent_r,
L465: 			       const struct crush_choose_arg *choose_args)
L470: 	const struct crush_bucket *in = bucket;
L473: 	int item = 0;
L476: 	int count = out_size;
L484: 	for (rep = stable ? 0 : outpos; rep < numrep && count > 0 ; rep++) {
L486: 		ftotal = 0;
L487: 		skip_rep = 0;
L489: 			retry_descent = 0;
L490: 			in = bucket;               /* initial bucket */
L493: 			flocal = 0;
L495: 				collide = 0;
L496: 				retry_bucket = 0;
L497: 				r = rep + parent_r;
L499: 				r += ftotal;
L502: 				if (in->size == 0) {
L503: 					reject = 1;
L506: 				if (local_fallback_retries > 0 &&
L507: 				    flocal >= (in->size>>1) &&
L508: 				    flocal > local_fallback_retries)
L509: 					item = bucket_perm_choose(
L510: 						in, work->work[-1-in->id],
L511: 						x, r);
L513: 					item = crush_bucket_choose(
L514: 						in, work->work[-1-in->id],
L515: 						x, r,
L516: 						(choose_args ?
L517: 						 &choose_args[-1-in->id] : NULL),
L518: 						outpos);
L519: 				if (item >= map->max_devices) {
L521: 					skip_rep = 1;
L526: 				if (item < 0)
L527: 					itemtype = map->buckets[-1-item]->type;
L529: 					itemtype = 0;
L533: 				if (itemtype != type) {
L534: 					if (item >= 0 ||
L535: 					    (-1-item) >= map->max_buckets) {
L537: 						skip_rep = 1;
L540: 					in = map->buckets[-1-item];
L541: 					retry_bucket = 1;
L546: 				for (i = 0; i < outpos; i++) {
L547: 					if (out[i] == item) {
L548: 						collide = 1;
L553: 				reject = 0;
L554: 				if (!collide && recurse_to_leaf) {
L555: 					if (item < 0) {
L557: 						if (vary_r)
L558: 							sub_r = r >> (vary_r-1);
L560: 							sub_r = 0;
L561: 						if (crush_choose_firstn(
L562: 							    map,
L563: 							    work,
L564: 							    map->buckets[-1-item],
L565: 							    weight, weight_max,
L566: 							    x, stable ? 1 : outpos+1, 0,
L567: 							    out2, outpos, count,
L568: 							    recurse_tries, 0,
L569: 							    local_retries,
L570: 							    local_fallback_retries,
L571: 							    0,
L572: 							    vary_r,
L573: 							    stable,
L574: 							    NULL,
L575: 							    sub_r,
L576: 							    choose_args) <= outpos)
L578: 							reject = 1;
L581: 						out2[outpos] = item;
L585: 				if (!reject && !collide) {
L587: 					if (itemtype == 0)
L588: 						reject = is_out(map, weight,
L589: 								weight_max,
L590: 								item, x);
L594: 				if (reject || collide) {
L595: 					ftotal++;
L596: 					flocal++;
L598: 					if (collide && flocal <= local_retries)
L600: 						retry_bucket = 1;
L601: 					else if (local_fallback_retries > 0 &&
L602: 						 flocal <= in->size + local_fallback_retries)
L604: 						retry_bucket = 1;
L605: 					else if (ftotal < tries)
L607: 						retry_descent = 1;
L610: 						skip_rep = 1;
L616: 			} while (retry_bucket);
L617: 		} while (retry_descent);
L619: 		if (skip_rep) {
L625: 		out[outpos] = item;
L626: 		outpos++;
L627: 		count--;
L629: 		if (map->choose_tries && ftotal <= map->choose_total_tries)
L630: 			map->choose_tries[ftotal]++;
L635: 	return outpos;
```

#### Function: `static int bucket_perm_choose(const struct crush_bucket *bucket,`

```c
L74: static int bucket_perm_choose(const struct crush_bucket *bucket,
L75: 			      struct crush_work_bucket *work,
L76: 			      int x, int r)
L78: 	unsigned int pr = r % bucket->size;
L82: 	if (work->perm_x != (__u32)x || work->perm_n == 0) {
L84: 		work->perm_x = x;
L87: 		if (pr == 0) {
L88: 			s = crush_hash32_3(bucket->hash, x, bucket->id, 0) %
L89: 				bucket->size;
L90: 			work->perm[0] = s;
L91: 			work->perm_n = 0xffff;   /* magic value, see below */
L95: 		for (i = 0; i < bucket->size; i++)
L96: 			work->perm[i] = i;
L97: 		work->perm_n = 0;
L98: 	} else if (work->perm_n == 0xffff) {
```

### File: `code/code_old/net/ceph/crush/hash.c`

#### Function: `__u32 crush_hash32_2(int type, __u32 a, __u32 b)`

```c
L104: __u32 crush_hash32_2(int type, __u32 a, __u32 b)
L106: 	switch (type) {
L107: 	case CRUSH_HASH_RJENKINS1:
L108: 		return crush_hash32_rjenkins1_2(a, b);
L110: 		return 0;
```

#### Function: `__u32 crush_hash32_3(int type, __u32 a, __u32 b, __u32 c)`

```c
L114: __u32 crush_hash32_3(int type, __u32 a, __u32 b, __u32 c)
L116: 	switch (type) {
L117: 	case CRUSH_HASH_RJENKINS1:
L118: 		return crush_hash32_rjenkins1_3(a, b, c);
L120: 		return 0;
```

#### Function: `__u32 crush_hash32_4(int type, __u32 a, __u32 b, __u32 c, __u32 d)`

```c
L124: __u32 crush_hash32_4(int type, __u32 a, __u32 b, __u32 c, __u32 d)
L126: 	switch (type) {
L127: 	case CRUSH_HASH_RJENKINS1:
L128: 		return crush_hash32_rjenkins1_4(a, b, c, d);
L13: #define crush_hashmix(a, b, c) do {			\
L130: 		return 0;
L25: #define crush_hash_seed 1315423911
```

#### Function: `static __u32 crush_hash32_rjenkins1_2(__u32 a, __u32 b)`

```c
L38: static __u32 crush_hash32_rjenkins1_2(__u32 a, __u32 b)
L40: 	__u32 hash = crush_hash_seed ^ a ^ b;
L41: 	__u32 x = 231232;
L42: 	__u32 y = 1232;
L43: 	crush_hashmix(a, b, hash);
L44: 	crush_hashmix(x, a, hash);
L45: 	crush_hashmix(b, y, hash);
L46: 	return hash;
```

#### Function: `static __u32 crush_hash32_rjenkins1_3(__u32 a, __u32 b, __u32 c)`

```c
L49: static __u32 crush_hash32_rjenkins1_3(__u32 a, __u32 b, __u32 c)
L51: 	__u32 hash = crush_hash_seed ^ a ^ b ^ c;
L52: 	__u32 x = 231232;
L53: 	__u32 y = 1232;
L54: 	crush_hashmix(a, b, hash);
L55: 	crush_hashmix(c, x, hash);
L56: 	crush_hashmix(y, a, hash);
L57: 	crush_hashmix(b, x, hash);
L58: 	crush_hashmix(y, c, hash);
L59: 	return hash;
```

#### Function: `static __u32 crush_hash32_rjenkins1_4(__u32 a, __u32 b, __u32 c, __u32 d)`

```c
L62: static __u32 crush_hash32_rjenkins1_4(__u32 a, __u32 b, __u32 c, __u32 d)
L64: 	__u32 hash = crush_hash_seed ^ a ^ b ^ c ^ d;
L65: 	__u32 x = 231232;
L66: 	__u32 y = 1232;
L67: 	crush_hashmix(a, b, hash);
L68: 	crush_hashmix(c, d, hash);
L69: 	crush_hashmix(a, x, hash);
L70: 	crush_hashmix(y, b, hash);
L71: 	crush_hashmix(c, x, hash);
L72: 	crush_hashmix(y, d, hash);
L73: 	return hash;
```

