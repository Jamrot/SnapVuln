### File: `code/code_old/drivers/nvme/target/tcp.c`

#### Function: `static void nvmet_tcp_free_cmd_data_in_buffers(struct nvmet_tcp_queue *queue)`

```c
L1579: static void nvmet_tcp_free_cmd_data_in_buffers(struct nvmet_tcp_queue *queue)
L1581: 	struct nvmet_tcp_cmd *cmd = queue->cmds;
L1584: 	for (i = 0; i < queue->nr_cmds; i++, cmd++) {
L1585: 		if (nvmet_tcp_need_data_in(cmd))
L1586: 			nvmet_tcp_free_cmd_buffers(cmd);
```

