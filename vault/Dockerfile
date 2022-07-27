FROM vault:1.10.3
LABEL Component="vault-server"

COPY vault-config.hcl /vault/config/vault-config.hcl
ENTRYPOINT ["vault"]

EXPOSE "8200"