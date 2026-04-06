# 虚拟机连接与 Virtuoso SKILL 操作指南

> 本文档记录了通过 virtuoso-bridge-lite 控制 Cadence Virtuoso 的完整操作流程，
> 包括 SSH 配置、bridge 启动、Python 连接模板以及常用 SKILL 操作。

---

## 环境概况

| 项目 | 值 |
|------|-----|
| 本地项目路径 | `C:\Users\qianx\Documents\GitHub\virtuoso-bridge-lite` |
| 虚拟机 IP | `192.168.171.128`（VMware NAT） |
| 虚拟机用户 | `IC`，密码 `123456` |
| 工艺库 | tsmc18 |

---

## 一、每次启动前的检查

### 1.1 确认虚拟机网卡已 UP

虚拟机重启后 `ens33` 可能未激活，需在 VMware 窗口内执行：

```bash
sudo ip link set ens33 up && sudo dhclient ens33
ip addr show ens33   # 确认出现 192.168.171.128
```

### 1.2 测试 SSH 连通性（Windows 端）

```bash
ssh IC@192.168.171.128 "echo OK"
```

---

## 二、SSH 免密登录配置（已完成，仅供参考）

密钥文件：`~/.ssh/id_ed25519_virtuoso`（Windows 端）

`~/.ssh/config` 中需有如下配置（非标准命名密钥不会自动使用）：

```
Host 192.168.171.128
    User IC
    IdentityFile ~/.ssh/id_ed25519_virtuoso
    IdentitiesOnly yes
```

公钥已写入虚拟机 `~/.ssh/authorized_keys`，权限：目录 700，文件 600。

> `.env` 中 `VB_SSH_KEY` 在代码里并无对应逻辑，SSH config 才是实际生效的方式。

---

## 三、Bridge 启动流程

```bash
# 步骤 1：在 VMware 窗口手动打开 Virtuoso（必须图形界面，不能 SSH 启动）

# 步骤 2：Windows 端启动 tunnel
cd C:/Users/qianx/Documents/GitHub/virtuoso-bridge-lite
uv run virtuoso-bridge start

# 步骤 3：在 Virtuoso CIW（Console）中执行（路径由 bridge start 输出给出）：
#   load("/tmp/virtuoso_bridge_IC/virtuoso_bridge/virtuoso_setup.il")

# 步骤 4：验证
uv run virtuoso-bridge status   # 应显示 [daemon] OK
```

---

## 四、Python 连接模板

```python
from dotenv import load_dotenv
load_dotenv()  # 工作目录需含 .env，或手动指定路径
from virtuoso_bridge.virtuoso.basic.bridge import VirtuosoClient

with VirtuosoClient.from_env() as v:
    result = v.execute_skill('...')
    print(result.output)   # SKILL 返回值
    print(result.errors)   # 错误列表（正常应为空）
```

> **注意：** 工作目录必须是项目根目录，或在 `load_dotenv()` 中指定 `.env` 的绝对路径。

---

## 五、常用 SKILL 片段

### 5.1 列出所有库

```skill
let((libs out)
  libs = ddGetLibList()
  out = ""
  foreach(lib libs out = strcat(out lib->name " "))
  out)
```

### 5.2 新建库并绑定 tech

```skill
ddCreateLib("myLib" "/home/IC/myLib")
let((lib)
  lib = car(setof(l ddGetLibList() l->name == "myLib"))
  lib->techLib = "tsmc18"
  t)
```

> **陷阱：** `techBindCDSLib` 和 `ddGetLib` 在该环境中未定义，获取库对象用 `setof(l ddGetLibList() ...)` + `car()`。

### 5.3 查看 instance 的 CDF 参数

```skill
let((cv inst cdf out)
  cv = dbOpenCellViewByType("libName" "cellName" "schematic" "" "r")
  inst = car(cv~>instances)
  cdf = cdfGetInstCDF(inst)
  out = ""
  foreach(param cdf->parameters
    out = strcat(out param->name "=" sprintf(nil "%L" param->value) " "))
  out)
```

### 5.4 修改器件参数（W/L 等）

```skill
let((cv inst cdf pw pl)
  cv = dbOpenCellViewByType("libName" "cellName" "schematic" "" "a")
  inst = car(cv~>instances)
  cdf = cdfGetInstCDF(inst)
  pw = cdfFindParamByName(cdf "w")
  pl = cdfFindParamByName(cdf "l")
  pw->value = "1u"
  pl->value = "1u"
  dbSave(cv)
  dbClose(cv)
  t)
```

> **陷阱：**
> - `cdfSetInstParam` 在该环境中**未定义**，必须用 `cdfFindParamByName` 取出参数对象后直接赋值 `->value`。
> - 打开模式必须用 `"a"`（可编辑），`"r"` 为只读，保存时会报错。

### 5.5 通过 Python 批量修改参数（完整示例）

```python
skill_code = """
let((cv inst cdf pw pl)
  cv = dbOpenCellViewByType("myLib" "myCell" "schematic" "" "a")
  inst = car(cv~>instances)
  cdf = cdfGetInstCDF(inst)
  pw = cdfFindParamByName(cdf "w")
  pl = cdfFindParamByName(cdf "l")
  pw->value = "2u"
  pl->value = "180n"
  dbSave(cv)
  dbClose(cv)
  t)
"""

with VirtuosoClient.from_env() as v:
    result = v.execute_skill(skill_code)
    print(result.output, result.errors)
```

---

## 六、可用 Tech Library（tsmc18 工艺环境）

```
cdsDefTechLib  basic  US_8ths  analogLib  functional
rfLib  rfExamples  ahdlLib  rfTlineLib
tsmcN65  tsmc18
```

---

## 七、已知问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| SSH 连接失败 | ens33 未激活 | 虚拟机内执行 `sudo ip link set ens33 up && sudo dhclient ens33` |
| SSH 仍需输密码 | 密钥未被识别 | 检查 `~/.ssh/config` 中是否有对应 Host 条目 |
| bridge status 失败 | CIW 中未 load setup.il | 在 Virtuoso CIW 中手动 load |
| SKILL 执行报 `undefined` | 函数名不对 | 参考本文档的陷阱说明 |
| dbSave 报错 | 以 `"r"` 模式打开 | 改用 `"a"` 模式打开 cellview |
