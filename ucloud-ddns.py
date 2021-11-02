import requests
import re
import hashlib


# 公钥，在控制台查询
public_key = ""
# 私钥，在控制台查询
private_key = ""
# 域名，如需解析 "test.github.com"， 则填入 github.com
domain = ""
# 主机名，如需解析 "test.github.com"， 则填入 test
hostname = ""
# 协议选择，仅可为 "ipv4", "ipv6", "ipv4/ipv6" 三种
protocol = ""



api_url = "http://api.ucloud.cn/"
record_type = {
    "ipv6": "AAAA",
    "ipv4": "A"
}


def get_signature(param: dict):
    string = ""
    for key in param:
        string += (key + str(param[key]))
    string += private_key
    return hashlib.sha1(string.encode("UTF-8")).hexdigest()


def get_local_ip(_record_type: str):
    if _record_type == "ipv6":
        response = requests.get("http://checkipv6.dyndns.com")
    elif _record_type == "ipv4":
        response = requests.get("http://checkip.dyndns.com")
    else:
        print("[Failed]wrong record type argument: " + _record_type)
        return None
    match = re.search("Address: (.*)</body>", response.text)
    if match:
        ip = match.group(1)
        print("[Success]local ip of " + _record_type + ": " + ip)
        return ip
    else:
        print("[Failed]unable to get local ip of " + _record_type +", check the Internet connection")
        return None


def get_all_recorded_ip(_record_type: str):
    param = {
        "Action": "UdnrDomainDNSQuery",
        "Dn": domain,
        "PublicKey": public_key
    }
    param["Signature"] = get_signature(param)
    response = requests.post(api_url, param).json()
    ans = []
    for case in response["Data"]:
        if case["DnsType"] == record_type[_record_type]:
            ans.append(case)
    return ans


def get_recorded_ip(_record_type: str):
    ans = get_all_recorded_ip(_record_type)
    for case in ans:
        if case["RecordName"] == (hostname + "." + domain):
            print("[Success]recorded ip address: " + case["Content"])
            return case["Content"]
    print("[Success]no address recorded on dns server")
    return None


def remove_recorded_ip(ip: str, _record_type: str):
    if not str:
        return
    param = {
        "Action": "UdnrDeleteDnsRecord",
        "Content": ip,
        "Dn": domain,
        "DnsType": record_type[_record_type],
        "PublicKey": public_key,
        "RecordName": hostname + "." + domain
    }
    param["Signature"] = get_signature(param)
    response = requests.post(api_url, param)
    if response.json()["RetCode"] == 0:
        print('[Success]invalid ip "' + ip + '" has been removed')
    else:
        print("[Failed]unable to remove record")


def update_record_ip(_record_type: str):
    print("trying to get local " + _record_type + " ip......")
    local_ip = get_local_ip(_record_type)
    if not local_ip:
        return
    print("trying to get recorded ip on server......")
    recorded_ip = get_recorded_ip(_record_type)
    if local_ip == recorded_ip:
        print("[Success]dns server already configured with the right address")
    else:
        if recorded_ip:
            print("removing invalid ip address recorded......")
            remove_recorded_ip(recorded_ip, _record_type)
        print("trying to send update request......")
        param = {
            "Action": "UdnrDomainDNSAdd",
            "Content": local_ip,
            "Dn": domain,
            "DnsType": record_type[_record_type],
            "PublicKey": public_key,
            "RecordName": hostname + "." + domain,
            "TTL": "600"
        }
        param["Signature"] = get_signature(param)
        response = requests.post(api_url, param)
        if response.json()["RetCode"] == 0:
            print("[Success]updated the ip address of " + _record_type + " on server")
        else:
            print("[Failed]update failed")


if protocol == "ipv4/ipv6":
    update_record_ip("ipv4")
    print("")
    update_record_ip("ipv6")
else:
    update_record_ip(protocol)
