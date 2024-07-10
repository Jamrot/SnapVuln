### File: `code/code_old/drivers/nvme/target/tcp.c`

#### Function: `static void nvmet_tcp_free_cmd_data_in_buffers(struct nvmet_tcp_queue *queue)`

```c
L1579: static void nvmet_tcp_free_cmd_data_in_buffers(struct nvmet_tcp_queue *queue)
L1581: 	struct nvmet_tcp_cmd *cmd = queue->cmds;
L1584: 	for (i = 0; i < queue->nr_cmds; i++, cmd++) {
L1585: 		if (nvmet_tcp_need_data_in(cmd))
L1586: 			nvmet_tcp_free_cmd_buffers(cmd);
```

#### Function: `static void nvmet_tcp_release_queue_work(struct work_struct *w)`

```c
L1593: static void nvmet_tcp_release_queue_work(struct work_struct *w)
L1599: 	list_del_init(&queue->queue_list);
L1602: 	nvmet_tcp_restore_socket_callbacks(queue);
L1603: 	cancel_delayed_work_sync(&queue->tls_handshake_tmo_work);
L1604: 	cancel_work_sync(&queue->io_work);
L1606: 	queue->rcv_state = NVMET_TCP_RECV_ERR;
L1608: 	nvmet_tcp_uninit_data_in_cmds(queue);
L1609: 	nvmet_sq_destroy(&queue->nvme_sq);
L1610: 	cancel_work_sync(&queue->io_work);
L1611: 	nvmet_tcp_free_cmd_data_in_buffers(queue);
L219: static void nvmet_tcp_free_cmd_buffers(struct nvmet_tcp_cmd *cmd);
```

#### Function: `static inline bool nvmet_tcp_need_data_in(struct nvmet_tcp_cmd *cmd)`

```c
L238: static inline bool nvmet_tcp_need_data_in(struct nvmet_tcp_cmd *cmd)
```

#### Function: `static void nvmet_tcp_free_cmd_buffers(struct nvmet_tcp_cmd *cmd)`

```c
L351: static void nvmet_tcp_free_cmd_buffers(struct nvmet_tcp_cmd *cmd)
```

