class Data:
    # Headers configuration
    default_headers = {
        "language": "en-EN",            # lang-LANG
        "romVersion": "unknown",        # ro.build.version.ota
        "otaVersion": "unknown",        # ro.build.version.ota
        "androidVersion": "unknown",    # Android{Version}
        "colorOSVersion": "unknown",    # ColorOS{Version}
        "model": "unknown",             # ro.product.name
        "infVersion": "1",              # N/A
        "operator": "unknown",          # ro.product.name
        "nvCarrier": "unknown",         # ro.build.oplus_nv_id
        "uRegion": "unknown",           # persist.sys.oppo.region (RUI1)
        "trackRegion": "unknown",       # ro.oppo.regionmark (RUI1)
        "imei": "000000000000000",      # IMEI
        "imei1": "000000000000000",     # IMEI
        "deviceId": "0",                # N/A
        "mode": "client_auto",          # Known values: "manual", "client_auto", "server_auto"
        "channel": "pc",                # Update channel
        "version": "1",                 # Request version
        "Accept": "application/json",   # N/A
        "Content-Type": "application/json", # N/A
        "User-Agent": "NULL"            # N/A
    }

    # Request body configuration
    default_body = {
        "language": "en-EN",            # lang-LANG
        "romVersion": "unknown",        # ro.build.version.ota
        "otaVersion": "unknown",        # ro.build.version.ota
        "androidVersion": "unknown",    # Android{Version}
        "colorOSVersion": "unknown",    # ColorOS{Version}
        "model": "unknown",             # ro.product.name
        "productName": "unknown",       # ro.product.name
        "operator": "unknown",          # ro.product.name
        "uRegion": "unknown",           # persist.sys.oppo.region (RUI1)
        "trackRegion": "unknown",       # ro.oppo.regionmark (RUI1)
        "imei": "000000000000000",      # IMEI
        "imei1": "000000000000000",     # IMEI
        "mode": "0",                    # 0 for normal, 1 for beta
        "registrationId": "unknown",    # N/A
        "deviceId": "0",                # N/A
        "version": "3",                 # N/A
        "type": "1",                    # N/A
        "otaPrefix": "unknown",         # ro.build.version.ota
        "isRealme": "unknown",          # N/A
        "time": "0",                    # N/A
        "canCheckSelf": "0"             # N/A
    }

    # URLs configuration
    urls = {
        1: {
            "GL": "https://ifota.realmemobile.com/post/Query_Update",    # GL
            "CN": "https://iota.coloros.com/post/Query_Update",          # CN
            "IN": "https://ifota-in.realmemobile.com/post/Query_Update", # IN
            "EU": "https://ifota-eu.realmemobile.com/post/Query_Update"  # EU
        },
        2: {
            "GL": "https://component-ota-f.coloros.com/update/v3",       # GL
            "CN": "https://component-ota.coloros.com/update/v3",         # CN
            "IN": "https://component-ota-in.coloros.com/update/v3",      # IN
            "EU": "https://component-ota-eu.coloros.com/update/v3"       # EU
        }
    }

    # Server parameters configuration
    class ServerConfig:
        def __init__(self, server_url, pub_key, negotiation_version):
            self.server_url = server_url
            self.pub_key = pub_key
            self.negotiation_version = negotiation_version

    server_params = {
        "GL": ServerConfig(
            server_url = "https://component-otapc-sg.allawnos.com/update/v3",
            pub_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkA980wxi+eTGcFDiw2I6RrUeO4jL/Aj3Yw4dNuW7tYt+O1sRTHgrzxPD9SrOqzz7G0KgoSfdFHe3JVLPN+U1waK+T0HfLusVJshDaMrMiQFDUiKajb+QKr+bXQhVofH74fjat+oRJ8vjXARSpFk4/41x5j1Bt/2bHoqtdGPcUizZ4whMwzap+hzVlZgs7BNfepo24PWPRujsN3uopl+8u4HFpQDlQl7GdqDYDj2zNOHdFQI2UpSf0aIeKCKOpSKF72KDEESpJVQsqO4nxMwEi2jMujQeCHyTCjBZ+W35RzwT9+0pyZv8FB3c7FYY9FdF/+lvfax5mvFEBd9jO+dpMQIDAQAB",
            negotiation_version = "1615895993238"
        ),
        "CN": ServerConfig(
            server_url = "https://component-otapc-cn.allawntech.com/update/v3",
            pub_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApXYGXQpNL7gmMzzvajHaoZIHQQvBc2cOEhJc7/tsaO4sT0unoQnwQKfNQCuv7qC1Nu32eCLuewe9LSYhDXr9KSBWjOcCFXVXteLO9WCaAh5hwnUoP/5/Wz0jJwBA+yqs3AaGLA9wJ0+B2lB1vLE4FZNE7exUfwUc03fJxHG9nCLKjIZlrnAAHjRCd8mpnADwfkCEIPIGhnwq7pdkbamZcoZfZud1+fPsELviB9u447C6bKnTU4AaMcR9Y2/uI6TJUTcgyCp+ilgU0JxemrSIPFk3jbCbzamQ6Shkw/jDRzYoXpBRg/2QDkbq+j3ljInu0RHDfOeXf3VBfHSnQ66HCwIDAQAB",
            negotiation_version = "1615879139745"
        ),
        "IN": ServerConfig(
            server_url = "https://component-otapc-in.allawnos.com/update/v3",
            pub_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwYtghkzeStC9YvAwOQmWylbp74Tj8hhi3f9IlK7A/CWrGbLgzz/BeKxNb45zBN8pgaaEOwAJ1qZQV5G4nProWCPOP1ro1PkemFJvw/vzOOT5uN0ADnHDzZkZXCU/knxqUSfLcwQlHXsYhNsAm7uOKjY9YXF4zWzYN0eFPkML3Pj/zg7hl/ov9clB2VeyI1/blMHFfcNA/fvqDTENXcNBIhgJvXiCpLcZqp+aLZPC5AwY/sCb3j5jTWer0Rk0ZjQBZE1AncwYvUx4mA65U59cWpTyl4c47J29MsQ66hqWv6eBHlDNZSEsQpHePUqgsf7lmO5Wd7teB8ugQki2oz1Y5QIDAQAB",
            negotiation_version = "1615896309308"
        ),
        "EU": ServerConfig(
            server_url = "https://component-otapc-eu.allawnos.com/update/v3",
            pub_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAh8/EThsK3f0WyyPgrtXb/D0Xni6UZNppaQHUqHWo976cybl92VxmehE0ISObnxERaOtrlYmTPIxkVC9MMueDvTwZ1l0KxevZVKU0sJRxNR9AFcw6D7k9fPzzpNJmhSlhpNbt3BEepdgibdRZbacF3NWy3ejOYWHgxC+I/Vj1v7QU5gD+1OhgWeRDcwuV4nGY1ln2lvkRj8EiJYXfkSq/wUI5AvPdNXdEqwou4FBcf6mD84G8pKDyNTQwwuk9lvFlcq4mRqgYaFg9DAgpDgqVK4NTJWM7tQS1GZuRA6PhupfDqnQExyBFhzCefHkEhcFywNyxlPe953NWLFWwbGvFKwIDAQAB",
            negotiation_version = "1615897067573"
        )
    }