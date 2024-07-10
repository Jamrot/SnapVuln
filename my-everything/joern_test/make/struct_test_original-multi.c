
struct ceph_frame_desc {
    int fd_lens[10];
};

struct ceph_connection_v2_info {
    struct ceph_frame_desc in_desc;
};

struct ceph_connection {
    union {
        struct ceph_connection_v2_info v2;
    };
};

static int decode_preamble(struct ceph_frame_desc *desc) {
    desc->fd_lens[0] = 0;
    return 0;
}

static int prepare_read_control(struct ceph_connection *con) {
    int ctrl_len = con->v2.in_desc.fd_lens[0];
    return 0;
}

static int handle_preamble(struct ceph_connection *con) {
    struct ceph_frame_desc *desc = &con->v2.in_desc;
    decode_preamble(desc); 
    prepare_read_control(con);
    return 0;
}

int main() {
    struct ceph_connection con;
    handle_preamble(&con);
    return 0;
}
