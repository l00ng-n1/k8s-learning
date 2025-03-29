# 数据存储

## 存储机制

Container 中的文件在磁盘上是临时存放的，这给 Container 中运行的较重要的应用程序带来一些问题。

-   当容器崩溃时。 kubelet 可能会重新创建容器，可能会导致容器漂移至新的宿主机，容器会以干净的状态重建。导致数据丢失
-   在同一 Pod 中运行多个容器需要共享数据

Kubernetes 卷（Volume） 这一抽象概念能够解决这两个问题

Kubernetes 集群中的容器数据存储

## Kubernetes支持的存储类型

[存储 | Kubernetes](https://kubernetes.io/zh-cn/docs/concepts/storage/)

Kubernetes支持丰富的存储类型，可以分为**树内**和**树外**两种

### 树内 In-Tree 存储卷插件

| 类型         | 举例                                                         |
| ------------ | ------------------------------------------------------------ |
| 临时存储卷   | emptyDir                                                     |
| 本地数据卷   | hostPath、local                                              |
| 文件系统     | NFS、CephFS、GlusterFS、fastdfs、Cinder、gitRepo(DEPRECATED) |
| 块设备       | iSCSI、FC、rdb(块设备)、vSphereVolume                        |
| 存储平台     | Quobyte、PortworxVolume、StorageOS、ScaleIO                  |
| 云存储数据卷 | Aliyun OSS、Amazon S3、AWS Elastic Block Store、Google gcePersistentDisk等 |
| 特殊存储卷   | ConfigMap、Secret、DownwardAPI、Projectd、flocker            |

### 树外 Out-of_Tree 存储卷插件

经由**容器存储接口CSI**或**FlexVolume接口（已淘汰）**扩展出的外部的存储系统称为Out-of-Trec类的存储插件

CSI 有多种实现,比如：

Rancher 是为使用容器的公司打造的容器管理平台。Rancher 简化了使用 Kubernetes 的流程，开发者可以随处运行 Kubernetes，满足IT 需求规范，赋能 DevOps 团队。这个团队研发的Longhorn就是要给非常好的存储平台。

Longhorn是一个轻量级且功能强大的云原生Kubernetes分布式存储平台，可以在任意基础设施上运行。Longhorn与Rancher结合使用，将帮助用户在Kubernetes环境中轻松、快速和可靠地部署高可用性持久化块存储。

**CSI 主要包含两个部分：CSI Controller Server 与 CSI Node Server，分别对应Controller Server Pod和Node Server Pod**

![image-20250329104909402](pic/image-20250329104909402.png)

*   Controller Server
    *   也称为CSI Controller
    *   在集群中只需要部署一个 Controller Server，以 deployment 或者 StatefulSet 的形式运行
    *   **CSI Controller Server**：负责卷的生命周期管理（如创建、删除、绑定、快照等），通常运行在 Kubernetes 控制平面或指定的控制节点上，即 **Controller Server Pod**；
    *   主要负责与存储服务API通信完成后端存储的管理操作，比如 provision 和 attach 工作。
*   Node Server
    *   也称为CSI Node 或 Node Plugin
    *   保证每一个节点会有一个 Pod 部署出来，负责在节点级别完成存储卷管理，和 CSI Controller 一起 完成 volume 的 mount 操作。
    *   Node Server Pod 是个 DaemonSet，它会在每个节点上进行注册。
    *   负责将卷挂载到本地节点，支持读写操作，通常部署在每个工作节点上，即 **Node Server Pod**。
    *   Kubelet 会直接通过 Socket 的方式直接和 CSI Node Server 进行通信、调用 Attach/Detach/Mount/Unmount 等。

![image-20250329105401937](pic/image-20250329105401937.png)

**CSI 插件包括以下两部分**

-   **CSI-Plugin**:实现数据卷的挂载、卸载功能。
-   **CSI-Provisioner**: 制备器（Provisioner）实现数据卷的自动创建管理能力，即驱动程序，比如: 支 持云盘、NAS等存储卷创建能力

## Kubernetes 存储架构

存储的组件主要有：attach/detach controller、pv controller、volume manager、volume plugins、 scheduler

![image-20250329105552428](pic/image-20250329105552428.png)

-   AD控制器：负责存储设备的Attach/Detach操作
    -   Attach：将设备附加到目标**节点**
    -   Detach：将设备从目标**节点**上卸载
-   **Volume Manager**：存储卷管理器，负责卷的 **挂载/卸载**（Mount/Unmount）到 Pod 的容器路径，以及设备的格式化操作等
-   **PV Controller** ：负责PV/PVC的绑定、生命周期管理，以及存储卷的Provision/Delete操作
-   volume plugins：包含k8s原生的和各厂商的的存储插件，扩展各种存储类型的卷管理能力
    -   原生的包括：emptydir、hostpath、csi等
    -   各厂商的包括：aws-ebs、azure等
-   scheduler：实现Pod的调度，涉及到volume的调度。比如ebs、csi关于单node最大可attach磁盘 数量的predicate策略，scheduler的调度至哪个指定目标节点也会受到存储插件的影响

## Pod的存储卷 volume

存储卷本质上表现为 **Pod中所有容器共享访问的目录**

而此目录的创建方式、使用的存储介质以及目录的初始内容是由Pod规范中声明的存储卷类型来源决定

**kubelet内置支持多种存储卷插件**，**存储卷是由各种存储插件(存储驱动)来提供存储服务**

存储卷插件(存储驱动)决定了支持的后端存储介质或存储服务，例如hostPath插件使用宿主机文件系 统，而nfs插件则对接指定的NFS存储服务等

Pod在规范中需要指定其包含的卷以及这些卷在容器中的挂载路径

**存储卷需要定义在指定的Pod之上**

有些卷本身的生命周期与Pod相同，但其后端的存储及相关数据的生命周期通常要取决于存储介质

存储卷可以分为：**临时卷和持久卷**

-   **临时卷类型**的生命周期与 Pod 相同， 当 Pod 不再存在时，Kubernetes 也会销毁临时卷
-   持久卷可以比 Pod 的存活期长。当 Pod 不再存在时，Kubernetes 不会销毁持久卷。
-   但对于给定 Pod 中任何类型的卷，在容器重启期间数据都不会丢失。

```shell
kubectl explain pod.spec.volumes
```

单节点存储

![image-20250329110328677](pic/image-20250329110328677.png)

多节点存储

![image-20250329110342359](pic/image-20250329110342359.png)

# Pod中卷的使用

-   一个Pod可以添加任意个卷
-   同一个Pod内每个容器可以在不同位置按需挂载Pod上的任意个卷，或者不挂载任何卷
-   同一个Pod上的某个卷，也可以同时被该Pod内的多个容器同时挂载，以共享数据
-   如果支持，多个Pod也可以通过卷接口访问同一个后端存储单元

![image-20250329110942130](pic/image-20250329110942130.png)

![image-20250329110948784](pic/image-20250329110948784.png)

**存储卷的配置由两部分组成**

-   通过.spec.volumes字段定义在Pod之上的存储卷列表，它经由特定的存储卷插件并结合特定的存储供给方的访问接口进行**定义**
-   嵌套定义在容器的volumeMounts字段上的存储卷挂载列表，它只能**挂载**当前Pod对象中定义的存储卷

**Pod 内部容器使用存储卷有两步：**

-   在Pod上定义存储卷，并关联至目标存储服务上**volumes**
    -   **定义卷**
-   在需要用到存储卷的容器上，挂载其所属的Pod中pause的存储卷**volumesMount**
    -   **引用卷**

**容器引擎对共享式存储设备的支持类型：**

-   **单路读写** - 多个容器内可以通过同一个中间容器对同一个存储设备进行读写操作
-   **多路并行读写** - 多个容器内可以同时对同一个存储设备进行读写操作
-   **多路只读** - 多个容器内可以同时对同一个存储设备进行只读操作

## Pod的卷资源对象属性

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: <string>
  namespace: <string>
spec:
  volumes:                       # 定义卷
  - name: <string>               # 存储卷名称标识，仅可使用DNS标签格式的字符，在当前Pod必须唯一
    VOL_TYPE: <Object>           # 存储卷插件及具体的目标存储供给方的相关配置
  containers:
  - name: ...
    image: ...
    volumeMounts:                # 挂载卷
    - name: <string>             # 要挂载的存储卷的名称，必须匹配存储卷列表中某项的定义
      mountPath: <string>        # 容器文件系统上的挂载点路径
      readOnly: <boolean>        # 是否挂载为只读模式，默认为"否"，即可读可写
      subPath: <string>          # 挂载存储卷上的一个子目录至指定挂载点
      subPathExpr: <string>      # 挂载有指定的模式匹配到的存储卷的文件或目录至挂载点
```

## emptyDir

**只在同一pod内多容器间共享数据，pod删除数据随之删除**

一个emptyDir volume在pod被调度到某个Node时候自动创建的，无需指定宿主机上对应的目录。 适用于在一个**Pod中不同容器间的临时数据的共享**

**emptyDir 数据存放在宿主机的路径如下**

```shell
/var/lib/kubelet/pods/<pod_id>/volumes/kubernetes.io~empty-dir/<volume_name>/<FILE>

#注意：此目录随着Pod删除，也会随之删除，不能实现持久化
```

**emptyDir 特点如下：**

-   此为**默认存储类型**
-   此方式只能临时存放数据，不能实现数据持久化
-   跟随Pod初始化而来，开始是空数据卷
-   Pod 被删除，emptyDir对应的宿主机目录也被删除，当然目录内的数据随之永久消除
-   emptyDir 数据卷介质种类跟当前主机的磁盘一样。
-   emptyDir 主机可以为同一个Pod内多个容器共享
-   emptyDir 容器数据的临时存储目录主要用于数据缓存和**同一个Pod内的多个容器共享使用**

### emptyDir属性解析

```shell
kubectl explain pod.spec.volumes.emptyDir
    medium       # 指定媒介类型，主要有default和memory两种
                 # 默认情况下，emptyDir卷支持节点上的任何介质，SSD、磁盘或网络存储，具体取决于自身所在Node的环境
                 # 将字段设置为Memory，让K8S使用tmpfs，虽然tmpfs快，但是Pod重启时，数据会被清除，并且设置的大小会被计入  # Container的内存限制当中
    sizeLimit    # 当前存储卷的空闲限制，默认值为nil表示不限制
    
kubectl explain pod.spec.containers.volumeMounts
    mountPath    # 挂载到容器中的路径,此目录会自动生成
    name         # 指定挂载的volumes名称
    readOnly     # 是否只读挂载
    subPath      # 是否挂载子目录的路径,默认不挂载子目录
```

### 配置示例

```yaml
# volume配置格式
volumes:
- name: volume_name
  emptyDir: {}
  
# volume使用格式
containers:
- volumeMounts:
  - name: volume_name
    mountPath: /path/to/container/  # 容器内路径


# 示例1
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - image: registry.k8s.io/test-webserver
    name: test-container
    volumeMounts:
    - mountPath: /cache
      name: cache-volume
  volumes:
  - name: cache-volume
    emptyDir: {} # 都为默认
    
# 示例2：
apiVersion: v1
kind: Pod
metadata:
  name: test-pd
spec:
  containers:
  - image: registry.k8s.io/test-webserver
    name: test-container
    volumeMounts:
    - mountPath: /cache
      name: cache-volume
  volumes:
  - name: cache-volume
    emptyDir:
      medium: Memory
      sizeLimit: 500Mi
```

### 在一个Pod中定义多个容器通过emptyDir共享数据

busybox容器写入index.html内容，nginx容器显示index.html

```yaml
vim storage-emptydir.yaml
apiVersion: v1
kind: Pod
metadata:
  name: storage-emptydir
spec:
  volumes:
  - name: nginx-data
    emptyDir: {}
  containers:
  - name: storage-emptydir-nginx
    image: harbor.l00n9.icu/public/nginx:stable-perl
    volumeMounts:
    - name: nginx-data
      mountPath: /usr/share/nginx/html/
  - name: storage-emptydir-busybox
    image: harbor.l00n9.icu/public/busybox:unstable-uclibc
    volumeMounts:
    - name: nginx-data
      mountPath: /data/
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do date > /data/index.html; sleep 1; done"
    
root@master1:~/k8s/storage# curl 10.244.2.55
Sat Mar 29 03:34:41 UTC 2025
root@master1:~/k8s/storage# curl 10.244.2.55
Sat Mar 29 03:34:42 UTC 2025
root@master1:~/k8s/storage# curl 10.244.2.55
Sat Mar 29 03:34:43 UTC 2025
root@master1:~/k8s/storage# curl 10.244.2.55
Sat Mar 29 03:34:44 UTC 2025
```

## hostPath

**只在同一node节点上多pod共享数据，数据保存在宿主机上**

hostPath 可以将**宿主机上的目录**挂载到 Pod 中作为数据的存储目录

**hostPath 一般用在如下场景：**

-   容器应用程序中某些文件需要永久保存
-   Pod删除，hostPath数据对应在宿主机文件不受影响,即hostPath的生命周期和Pod不同,而和节点相同
-   **宿主机和容器的目录都会自动创建**
-   某些容器应用需要用到容器的自身的内部数据，可将宿主机的/var/lib/[docker|containerd]挂载到 Pod中

**hostPath 使用注意事项：**

-   不同宿主机的目录和文件内容不一定完全相同，所以Pod迁移前后的访问效果不一样
-   不适合Deployment这种分布式的资源，更适合于DaemonSet
-   宿主机的目录不属于独立的资源对象的资源，所以**对资源设置的资源配额限制对hostPath目录无效**

### 配置属性

```yaml
# 配置属性
kubectl explain pod.spec.volumes.hostPath
path                         # 指定哪个宿主机的目录或文件被共享给Pod使用
type                         # 指定路径的类型，一共有7种，默认的类型是没有指定
     空字符串                 # 默认配置，在关联hostPath存储卷之前不进行任何检查，如果宿主机没有对应的目录，会自动创建
     DirectoryCreate         # 宿主机上不存在，创建此0755权限的空目录，属主属组均为kubelet
     Directory               # 必须存在，挂载已存在目录
     FileOrCreate            # 宿主机上不存在挂载文件，就创建0644权限的空文件，属主属组均为kubelet
     File                    # 必须存在文件
     Socket                  # 事先必须存在Socket文件路径
     CharDevice              # 事先必须存在的字符设备文件路径
     BlockDevice             # 事先必须存在的块设备文件路径
     
     
# 配置格式：
  volumes:
  - name: volume_name
    hostPath:
      path: /path/to/host
      
# 示例：
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  spec:
    containers:
    - image: registry.k8s.io/test-webserver
      name: test-container
      volumeMounts:
      - mountPath: /test-pod
        name: test-volume
    volumes:
    - name: test-volume
      hostPath:
        path: /data           # 宿主机上目录位置
        type: Directory       # 此字段为可选
```

###  Redis 数据的持久化

如果第二次分配到不同的node节点，数据无法持久化

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: redis
spec:
  # nodeName: node1.l00n9.icu #指定运行在指定worker主机上
  containers:
  - name: redis
    image: harbor.l00n9.icu/public/redis:8.0-alpine
    imagePullPolicy: IfNotPresent
    volumeMounts:
    - name: redisdata
      mountPath: /data
  volumes:
  - name: redisdata
    hostPath:
      type: DirectoryOrCreate
      path: /data/redis
```

## NFS存储

### NFS 安装

#### pod

```yaml
vim storage-nfs-server.yaml
---
apiVersion: v1
kind: Service
metadata:
  name: nfs-server
  labels:
    app: nfs-server
spec:
  type: ClusterIP
  selector: 
    app: nfs-server
  ports:
    - name: tcp-2049            # 未显示指定tartPort，默认和port一致
      port: 2049
      protocol: TCP
    - name: udp-111
      port: 111
      protocol: UDP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nfs-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nfs-server
  template:
    metadata:
      name: nfs-server
      labels:
        app: nfs-server
    spec:
      nodeSelector:
        "kubernetes.io/os": linux
        "server": nfs                 # 需要在一个node节点上打上server=nfs标签
      containers:
      - name: nfs-server
        image: harbor.l00n9.icu/public/nfs-server-alpine:12
        env:
        - name: SHARED_DIRECTORY
          value: "/exports"
        volumeMounts:
        - mountPath: /exports
          name: nfs-vol
        securityContext:
          privileged: true
        ports:                       # 声明性说明，无直接功能，除非Service配置了targetPort匹配这些端口
        - name: tcp-2049
          containerPort: 2049
          protocol: TCP
        - name: udp-111
          containerPort: 111
          protocol: UDP
      volumes:
      - name: nfs-vol
        hostPath:
          path: /nfs-vol
          type: DirectoryOrCreate
```

#### 服务

服务端

```yaml
#NFS服务器软件安装服务端包,10.0.0.109
apt install nfs-kernel-server

#配置共享目录
mkdir /nfs-data
echo '/nfs-data *(rw,all_squash,anonuid=0,anongid=0)' >> /etc/exports
# 或
echo '/nfs-data *(rw,no_root_squash)' >> /etc/exports

# 加载配置
exportfs -r
# 查看配置
exportfs -v
```

客户端

```yaml
# 在每个节点上安装客户端包，包括master
apt install nfs-common

# DNS配置解析地址或使用hosts解析
vim /etc/hosts
10.0.0.109 harbor.l00n9.icu  harbor  nfs.l00n9.icu nfs 

# 测试
showmount -e nfs.l00n9.icu
Export list for nfs.l00n9.icu:
/nfs-data *
```

### 网络共享存储 NFS

和传统的方式一样, 通过 NFS 网络文件系统可以实现Kubernetes数据的网络存储共享

使用NFS提供的共享目录存储数据时，需要在系统中部署一个NFS环境，通过volume的配置，实现pod 内的容器间共享NFS目录。

```yaml
cat storage-nfs-1.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: storage

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-nfs
  namespace: storage
  labels:
    app: nginx-nfs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx-nfs
  template:
    metadata:
      labels:
        app: nginx-nfs
    spec:
      volumes:
      - name: html
        nfs:
          server: nfs.l00n9.icu
          path: /nfs-data/nginx
      containers:
      - image: harbor.l00n9.icu/public/nginx:stable-perl
        name: nginx
        volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html
          
# 注意：nfs中的域名解析，使用的式Node上的DNS，而不是COREDNS，所以需要在Node节点上将DNS指向私有DNS

# nfs服务器上
echo v0.1 > /nfs-data/nginx/index.html
# 访问测试

echo v0.2 > /nfs-data/nginx/index.html
# 访问测试
```

