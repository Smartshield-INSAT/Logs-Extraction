@load base/protocols/conn
@load base/protocols/http
@load base/protocols/dns
@load base/protocols/ftp
@load base/protocols/ssh

module ExtractFeatures;

export {
    # Define a new logging stream
    redef enum Log::ID += { LOG };

    # Connection state tracking
    global conn_state_tracker: table[addr, addr] of count &create_expire = 5 mins;

    # Define a global variable for the log directory, with a default value
    global log_dir: string &redef;

    # Define the log record structure
    type Info: record {
        ts: time &log;                    # Stime (25)
        uid: string &log;
        srcip: addr &log;                 # srcip (1)
        sport: port &log;                 # sport (2)
        dstip: addr &log;                 # dstip (3)
        dsport: port &log;                # dsport (4)
        service: string &log;             # service (14)
        proto: string &log &default="-";  # proto (5)
        trans_depth: count &log &default=0;  # Transaction depth for HTTP
        is_sm_ips_ports: count &log &default=0;    # is_sm_ips_ports (30)
        ct_flw_http_mthd: count &log &default=0;  # ct_flw_http_mthd (32)
        is_ftp_login: count &log &default=0;       # is_ftp_login (33)
    };
}

event zeek_init() {
    local output_dir = log_dir == "" ? "ALERT" : log_dir;
    Log::create_stream(ExtractFeatures::LOG, 
        [$columns=Info, 
         $path=output_dir]
    );
    # Disable logs for common Zeek protocols and activities
    Log::disable_stream(Conn::LOG);      # conn.log: Connection information (IP addresses, ports, protocols, durations)
    Log::disable_stream(DNS::LOG);       # dns.log: DNS queries and responses
    Log::disable_stream(HTTP::LOG);      # http.log: HTTP requests and responses
    Log::disable_stream(Files::LOG);     # files.log: File transfer activities over the network
    Log::disable_stream(SSL::LOG);       # ssl.log: SSL/TLS session information
    Log::disable_stream(X509::LOG);      # x509.log: X.509 certificate details
    Log::disable_stream(SMTP::LOG);      # smtp.log: SMTP session-level activity (email traffic)
    Log::disable_stream(FTP::LOG);       # ftp.log: FTP session details
    Log::disable_stream(Weird::LOG);     # weird.log: Logs unusual or unexpected events detected by Zeek
    Log::disable_stream(SNMP::LOG);      # snmp.log: SNMP traffic and related information
    Log::disable_stream(DHCP::LOG);      # dhcp.log: DHCP transactions and leases
    Log::disable_stream(SSH::LOG);       # ssh.log: SSH session details
    #packet filter disable
    Log::disable_stream(PacketFilter::LOG); # packet_filter.log: Logs packet filter activity
    }

# Helper function to determine protocol
function get_protocol(c: connection): string {
    if ( c?$conn ) {
        if ( c$conn?$proto ) {
            return fmt("%s", c$conn$proto);
        }
    }
    return "-";
}

# Update connection state tracking
function update_conn_tracking(c: connection) {
    local src = c$id$orig_h;
    local dst = c$id$resp_h;

    if ([src, dst] !in conn_state_tracker)
        conn_state_tracker[src, dst] = 0;
        
    conn_state_tracker[src, dst] += 1;
}

event connection_state_remove(c: connection) {
    local is_sm_ips_ports: count = 0;
    
    if (c$id$orig_h == c$id$resp_h && c$id$orig_p == c$id$resp_p) {
        is_sm_ips_ports = 1;
    }

    local info: Info = [
        $ts = c$start_time,
        $uid = c$uid,
        $srcip = c$id$orig_h,
        $sport = c$id$orig_p,
        $dstip = c$id$resp_h,
        $dsport = c$id$resp_p,
        $service = (c?$conn && c$conn?$service) ? c$conn$service : "-",
        $proto = get_protocol(c),
        $is_sm_ips_ports = is_sm_ips_ports
    ];
    
    Log::write(LOG, info);
}

# Handle HTTP requests
event http_request(c: connection, method: string, original_URI: string,
                  unescaped_URI: string, version: string) {

    update_conn_tracking(c);
    
    local is_sm_ips_ports: count = 0;
    if (c$id$orig_h == c$id$resp_h && c$id$orig_p == c$id$resp_p) {
        is_sm_ips_ports = 1;
    }

    local info: Info = [
        $ts = network_time(),
        $uid = c$uid,
        $srcip = c$id$orig_h,
        $sport = c$id$orig_p,
        $dstip = c$id$resp_h,
        $dsport = c$id$resp_p,
        $service = "http",
        $proto = get_protocol(c),
        $trans_depth = c$http$trans_depth,
        $ct_flw_http_mthd = conn_state_tracker[c$id$orig_h, c$id$resp_h],
        $is_sm_ips_ports = is_sm_ips_ports
    ];
    
    Log::write(LOG, info);
}

# Handle FTP commands
event ftp_request(c: connection, command: string, arg: string) {
    if (command == "PASS") {
        local is_ftp_login = 1;
        
        local is_sm_ips_ports: count = 0;
        if (c$id$orig_h == c$id$resp_h && c$id$orig_p == c$id$resp_p) {
            is_sm_ips_ports = 1;
        }
        
        local info: Info = [
            $ts = network_time(),
            $uid = c$uid,
            $srcip = c$id$orig_h,
            $sport = c$id$orig_p,
            $dstip = c$id$resp_h,
            $dsport = c$id$resp_p,
            $service = "ftp",
            $proto = get_protocol(c),
            $is_ftp_login = is_ftp_login,
            $is_sm_ips_ports = is_sm_ips_ports
        ];
        
        Log::write(LOG, info);
    }
}
