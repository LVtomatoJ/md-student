---
create_time: 2025-05-09 20:03:58
tags: web3
title: "基于长安链实现商品溯源"
update_time: 2025-05-09 20:03:59

---


# 基于长安链实现商品溯源

## 1. 概述

毕设时本来想做基于BSN的区块链Dapp但是后来遇到各种各样的bug最后放弃了选择了直接在以太坊开发。过去一年了想看看长安链进展怎么样,实测国产区块链依旧很多很多坑,国产区块链依旧有很长的路要走(不是),刚好记录一下这个demo的过程。因为是demo所以没有深入的研究各种各样的问题（保命）

## 2. 环境搭建

首先本文基于v2.3.6进行搭建，建议萌新先通过官方文档来走。
[官网文档首页](https://docs.chainmaker.org.cn/v2.3.6/html/index.html)

- 系统环境:CentOS 7.6 (我也不想用远古系统啊 官网这么写的 qwq)
- 硬件环境: 2核4G (2g卡飞了4g内存起步)
- 其实是腾讯云x86 (不是我不想在本机跑 是mac+arm遇到了太多坑放弃了 但是腾讯云的OrcaTerm确实好评)

### 安装git

```bash
# 安装git
sudo yum install git
```

### 安装golang

好的遇到了墙内人第一个障碍安装golang1.19
已经丢在cf里了自提 [下载地址](https://download.blog.lvtomatoj.com/go1.19.linux-amd64.tar.gz)
go安装文档[地址](https://go.dev/doc/install)

```bash
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.19.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
go version
# 看到版本号就成功啦
```

### 升级gcc

```bash
sudo yum install centos-release-scl
sudo yum install devtoolset-7-gcc*
```

第二步错了吧哈哈哈哈哈哈哈哈哈,虽然官网这么写但是跑不起来,centos7.6老古董了理解理解。想起来一件招笑的事用orcateam的ai助手他让我换阿里云的镜像源（你不是腾讯的崽吗hh
其实原因就是7.6已经被归档了 所以官方库的地址已经到vault.centos.org了 那为什么其他的能yum install成功呢，因为CentOS-Base.repo是正确的但是SCL的仓库还是访问不到
[参考文章](https://zhuanlan.zhihu.com/p/719952763)

修改CentOS-SCLo-scl.repo

```text
[centos-sclo-sclo]
name=CentOS-$releasever - SCLo sclo
baseurl=https://mirrors.cloud.tencent.com/centos/$releasever/sclo/x86_64/sclo/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
```

修改CentOS-SCLo-scl-rh.repo

```text
[centos-sclo-rh]
name=CentOS-$releasever - SCLo rh
baseurl=https://mirrors.cloud.tencent.com/centos/$releasever/sclo/x86_64/rh/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
```

```bash
yum clean all
yum makecache
cd /etc/yum.repos.d
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-SIG-SCLo
rpm -qi gpg-pubkey-f2ee9d55
yum clean all
yum makecache
sudo yum install devtoolset-7-gcc*
scl enable devtoolset-7 bash
```

## 3. 长安链！启动

好吧启动之前先了解一下文档中列举的方法

- 通过命令行启动(明智之选)
- 通过控制台体验(尝试过但放弃...)
- 长安链开放测试网络(没开放...)

先甩出[官方文档地址](https://docs.chainmaker.org.cn/v2.3.6/html/quickstart/%E9%80%9A%E8%BF%87%E5%91%BD%E4%BB%A4%E8%A1%8C%E4%BD%93%E9%AA%8C%E9%93%BE.html)

chainmaker-go是长安链启动的核心仓库但是居然要账号注册才给下载..无力吐槽并丢出一个[zip链接](https://download.blog.lvtomatoj.com/chainmaker-go-master.zip)

### 准备文件&编译证书生成工具

```bash
# 解压chainmaker-go-master.zip
unzip chainmaker-go-master.zip
# clone 证书生成工具
git clone -b v2.3.5 --depth=1 https://git.chainmaker.org.cn/chainmaker/chainmaker-cryptogen.git
# 编译证书生成工具
cd chainmaker-cryptogen
# 编译之前 先给go套上镜像...
export GOPROXY=https://goproxy.cn,direct
# 编译证书生成工具
make
```

### 启动节点

```bash
# 软连接证书生成工具
cd chainmaker-go-master/tools
ln -s ../../chainmaker-cryptogen/ .
cd ../scripts
# 生成证书
./prepare.sh 4 1
# 编译&制作节点安装包
./build_release.sh
# 启动节点集群
./cluster_quick_start.sh normal
```

此时可以看到后台已经运行了四个节点

```bash
ps -ef|grep chainmaker | grep -v grep
```

至此启动成功，需要特别注意的是，在chainmaker-go-master目录下会生成一个build目录，其中的**crypto-config**文件夹包含了所有必要的证书。这些证书在后续的合约部署以及SDK调用中都是必不可少的。

## 4、合约编码与部署

既然官方都用了rust的合约那我们也用rust来尝试吧，[使用rust开发合约](https://docs.chainmaker.org.cn/v2.3.6/html/instructions/%E4%BD%BF%E7%94%A8Rust%E8%BF%9B%E8%A1%8C%E6%99%BA%E8%83%BD%E5%90%88%E7%BA%A6%E5%BC%80%E5%8F%91.html)

rust的安装和编译我都是在本地做的因为实在不想折腾网络环境了,以下为文档的安装说明

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# 让 Rust 的环境变量生效 
source "$HOME/.cargo/env"
# 加入 wasm32-unknown-unknown
rustup target add wasm32-unknown-unknown
```

### 合约编写

合约的规范建议参考官方文档这里给出几个示例
首先我们的需求是实现一个简单的商品溯源系统，需要包含几个组织(生产商、物流、质检、监管)，这里的四个就刚好对应了生成的四个节点的四个组织,所以在合约的开头先进行一下定义

```rust
const ROLE_MANUFACTURER: &str = "wx-org1.chainmaker.org";
const ROLE_LOGISTICS: &str = "wx-org2.chainmaker.org";
const ROLE_QUALITY_INSPECTION: &str = "wx-org3.chainmaker.org";
const ROLE_REGULATOR: &str = "wx-org4.chainmaker.org";
```

其次是结构体，包含了批次信息结构体、运输记录结构体、质检报告结构体

```rust
#[derive(Clone)]
struct Batch {
    batch_id: String,
    product_name: String,
    manufacturer: String,
    production_date: String,
    expiry_date: String,
    status: String,
}

impl Batch {
    fn from_ec(ec: &EasyCodec) -> Self {
        Batch {
            batch_id: ec.get_string("batch_id").unwrap_or_default(),
            product_name: ec.get_string("product_name").unwrap_or_default(),
            manufacturer: ec.get_string("manufacturer").unwrap_or_default(),
            production_date: ec.get_string("production_date").unwrap_or_default(),
            expiry_date: ec.get_string("expiry_date").unwrap_or_default(),
            status: ec.get_string("status").unwrap_or_default(),
        }
    }

    fn to_ec(&self) -> EasyCodec {
        let mut ec = EasyCodec::new();
        ec.add_string("batch_id", &self.batch_id);
        ec.add_string("product_name", &self.product_name);
        ec.add_string("manufacturer", &self.manufacturer);
        ec.add_string("production_date", &self.production_date);
        ec.add_string("expiry_date", &self.expiry_date);
        ec.add_string("status", &self.status);
        ec
    }

    fn to_json(&self) -> String {
        format!(
            "{{\"batch_id\":\"{}\",\"product_name\":\"{}\",\"manufacturer\":\"{}\",\"production_date\":\"{}\",\"expiry_date\":\"{}\",\"status\":\"{}\"}}",
            self.batch_id, self.product_name, self.manufacturer, self.production_date, self.expiry_date, self.status
        )
    }
}
```

接下来是合约函数了这里列举一个插入一个查询

```rust
// 添加运输记录
#[no_mangle]
pub extern "C" fn add_transport_record() {
    let ctx = &mut sim_context::get_sim_context();
    
    // 获取调用者组织ID
    let org_id = ctx.get_sender_org_id();
    
    if org_id != ROLE_LOGISTICS {
        ctx.error("Permission denied: only Logistics can handle transport records.");
        return;
    }
    
    // 获取参数
    let record_id = ctx.arg_as_utf8_str("record_id");
    let batch_id = ctx.arg_as_utf8_str("batch_id");
    let from = ctx.arg_as_utf8_str("from");
    let to = ctx.arg_as_utf8_str("to");
    let carrier = ctx.arg_as_utf8_str("carrier");
    let start_time = ctx.arg_as_utf8_str("start_time");
    let end_time = ctx.arg_as_utf8_str("end_time");
    let temperature = ctx.arg_as_utf8_str("temperature");
    
    // 创建EasyCodec并添加值
    let mut ec = EasyCodec::new();
    ec.add_string("record_id", &record_id);
    ec.add_string("batch_id", &batch_id);
    ec.add_string("from", &from);
    ec.add_string("to", &to);
    ec.add_string("carrier", &carrier);
    ec.add_string("start_time", &start_time);
    ec.add_string("end_time", &end_time);
    ec.add_string("temperature", &temperature);
    
    let record = TransportRecord::from_ec(&ec);
    let res = ctx.get_state("batch", &record.batch_id);
    if res.is_err() {
        ctx.error("读取批次信息失败");
        return;
    }
    let batch_bytes = res.unwrap();
    if batch_bytes.is_empty() {
        ctx.error("Batch not found.");
        return;
    }
    let record_ec = record.to_ec();
    
    // 键名只包含实际的标识符部分，不要包含命名空间前缀
    let key = format!("t_{}_{}",record.batch_id, record.record_id);

    // 修改：使用put_state_from_key而非put_state，避免命名空间问题
    let res = ctx.put_state_from_key(&key, &record_ec.marshal());
    if res != 0 {
        ctx.error("Failed to store transport record.");
        return;
    }

    ctx.ok("Transport record added successfully.".as_bytes());
}

// 查询运输记录
#[no_mangle]
pub extern "C" fn query_transport_records() {
    let ctx = &mut sim_context::get_sim_context();
    
    // 获取调用者组织ID
    let org_id = ctx.get_sender_org_id();
    
    if org_id != ROLE_LOGISTICS && org_id != ROLE_REGULATOR {
        ctx.error("Permission denied: only Logistics or Regulator can query transport records.");
        return;
    }
    
    let batch_id = ctx.arg_as_utf8_str("batch_id");
    
    // 构建前缀字符串
    let prefix = format!("t_{}_", batch_id);

    // 使用前缀迭代器查询
    let transport_iter_res = ctx.new_iterator_prefix_with_key(&prefix);
    
    if transport_iter_res.is_err() {
        ctx.error("Failed to get transport records.");
        return;
    }
    
    let iterator = transport_iter_res.unwrap();
    let mut records_vec = Vec::new();
    
    while iterator.has_next() {
        let row_result = iterator.next_row();
        if row_result.is_err() {
            continue;
        }
        
        let row = row_result.unwrap();
        if let Ok(value_bytes) = row.get_bytes("value") {
            let ec = EasyCodec::new_with_bytes(&value_bytes);
            let record = TransportRecord::from_ec(&ec);
            records_vec.push(record);
        }
    }
    
    // 构建JSON响应
    let mut json_response = String::from("[");
    for (i, record) in records_vec.iter().enumerate() {
        if i > 0 {
            json_response.push_str(",");
        }
        json_response.push_str(&record.to_json());
    }
    json_response.push_str("]");

    // 返回JSON格式数据
    ctx.ok(json_response.as_bytes());
}
```

### 编译合约

编译时需要在合约目录存在Cargo.toml 这里给一个示例

```toml
[package]
name = "rust-contract"
version = "0.1.0"
edition = "2021"

[dependencies]
contract_sdk_rust = { git = "https://git.chainmaker.org.cn/chainmaker/contract-sdk-rust", tag = "v2.3.0" }

[lib]
name = "rust_contract"
path = "food_trace.rs"
crate-type = ["cdylib"]
```

运行编译

```bash
cargo build --release --target=wasm32-unknown-unknown
```

编译完成后会在target/release目录里生成一个wasm文件 这个就是我们要用到合约

### 部署合约

部署合约需要使用到cmc工具来演示一下这个在chainmaker-go的tools目录中

```bash
# 编译cmc
cd chainmaker-go-master/tools/cmc
go build
# cp crypto-config
cp -rf ../../build/crypto-config ../../tools/cmc/testdata/
```

下来将wasm文件放在cmc目录里方便调用然后执行以下命令
需要将contact-name 修改为你想设置的合约名称，然后将byte-code-path修改为编译后的wasm文件路径即可

```bash
./cmc client contract user create \
--contract-name=food_trace \
--runtime-type=WASMER \
--byte-code-path=./rust_contract.wasm \
--version=1.0 \
--sdk-conf-path=./testdata/sdk_config.yml \
--admin-key-file-paths=./testdata/crypto-config/wx-org1.chainmaker.org/user/admin1/admin1.sign.key,./testdata/crypto-config/wx-org2.chainmaker.org/user/admin1/admin1.sign.key,./testdata/crypto-config/wx-org3.chainmaker.org/user/admin1/admin1.sign.key \
--admin-crt-file-paths=./testdata/crypto-config/wx-org1.chainmaker.org/user/admin1/admin1.sign.crt,./testdata/crypto-config/wx-org2.chainmaker.org/user/admin1/admin1.sign.crt,./testdata/crypto-config/wx-org3.chainmaker.org/user/admin1/admin1.sign.crt \
--sync-result=true \
--params="{}"
```

## 5、使用SDK调用合约

官方支持的sdk有Go Java Python Nodejs和Python,这里选用了最熟悉的Python

[Python SDK文档](https://docs.chainmaker.org.cn/v2.3.6/html/sdk/PythonSDK%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E.html)

要求版本python在3.9.0以上需要编译安装这里自行研究一下吧 丢一个[Python3.9.22源码包](https://download.blog.lvtomatoj.com/Python-3.9.22.tgz)

```bash
pip3 install git+https://git.chainmaker.org.cn/chainmaker/sdk-python.git
```

### 调用示例

首先需要创建ChainClient,因为我们有四个组织对应不同的权限所以封装成了class

```python
class Manufacturer:
    def __init__(self):
        self.cc = ChainClient.from_conf('./testdata/sdk_config_org1.yml')

    def create_batch(self, batch_id: str, product_name: str, manufacturer: str, production_date: str, expiry_date: str):
        print(f"创建批次 - 批次ID: {batch_id}")
        res1 = self.cc.invoke_contract(contract_name, 'create_batch', {"batch_id":batch_id,"product_name":product_name,"manufacturer":manufacturer,"production_date":production_date,"expiry_date":expiry_date},
                          with_sync_result=True)
        return res1
        
    def query_batch(self, batch_id: str):
        print(f"查询批次 - 批次ID: {batch_id}")
        res = self.cc.invoke_contract(contract_name, 'query_batch', {"batch_id":batch_id},
                          with_sync_result=True)
        return res
```

Tips:

- testdata目录与cmc目录下cp的一致 但是需要格外不同org的sdk_config如这里用到的sdk_config_org1就是对应的生产商和对应的证书
- 这里需contract_name为用cmc上床合约时制定的名称字符串

合约返回的结果是Protobuf所以还需要转换为Python中的字典

```Python
from google.protobuf import json_format
json_string = json_format.MessageToJson(proto_obj,preserving_proto_field_name=True)
result = json.loads(json_string)
```

接下来提取字典中base64编码的结果并转换成json下面给出一个接口完整的示例

```python
@app.post("/api/manufacturer/query_batch")
async def query_batch(batch_id: str = Form(...)):
    try:
        print(f"API调用: 查询批次 - 批次ID: {batch_id}")
        result = manufacturer.query_batch(batch_id=batch_id)
        # 转换Protobuf对象为字典
        result_dict = convert_proto_to_dict(result)
        
        # 从合约结果中提取JSON数据
        batch_data = {}
        if "contract_result" in result_dict and "result" in result_dict["contract_result"]:
            # 从Base64解码JSON字符串
            decoded_bytes = base64.b64decode(result_dict["contract_result"]["result"])
            json_str = decoded_bytes.decode('utf-8', errors='replace')
            # 尝试解析JSON
            try:
                batch_data = json.loads(json_str)
                print(f"成功解析JSON数据: {batch_data}")
            except json.JSONDecodeError as je:
                print(f"JSON解析错误: {str(je)}")
                # 如果JSON解析失败，返回一个默认的批次数据结构
                batch_data = {
                    "batch_id": batch_id,
                    "product_name": "数据格式不兼容",
                    "manufacturer": "数据格式不兼容",
                    "production_date": "",
                    "expiry_date": "",
                    "status": "未知",
                    "error": f"JSON解析失败: {str(je)}"
                }
        return {"success": True, "message": "查询批次成功", "data": batch_data}
    except Exception as e:
        print(f"查询批次失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

至此SDK的调用也完成了

## 总

其实这个demo整体跑下来花了蛮多时间的(7h+),一开始想在arm上跑但是遇到了各种难题，尝试控制台部署也是奇奇怪怪的问题，而且自己的能力没有办法支持深入阅读源码去解决，但是好在最后也是顺利完成了部署和开发。后续在Web3中我会更想尝试solana的开发，看看有没有什么更好的点子可以实现在区块链！另外Go和Rust作为补充需要提高提高了！
