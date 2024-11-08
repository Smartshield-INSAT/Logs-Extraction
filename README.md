# Logs-Extraction

## OpenArgus
You need to have argus installed, refer to https://github.com/openargus/argus.
Preferrably https://github.com/openargus/argus/blob/main/Dockerfile for container environment


## Zeek
you can opt for many installation methods as well, see https://docs.zeek.org/en/current/install.html

Or you can directly use the provided Dockerfile to have zeek and argus already installed and working

## Python dependencies (for manual or docker installation)

Run 
```bash
pip install -r requirements.txt
```

## USAGE:
```bash 
./process_pcap.sh PCAPNAME.pcap
```