# StatefulSet

## **无状态 和 有状态**

-   **无状态（Stateless）**

    无状态的系统不会在多个请求之间保存任何状态信息。每个请求都独立处理，不考虑之前的请求或状态。

    无状态的每次的请求都是独立的，它的执行情况和结果与前面的请求和之后的请求是无直接关系 的，它不会受前面的请求应答情况直接影响，也不会直接影响后面的请求应答情况

    典型的无状态系统包括HTTP协议、RESTful API等。每个请求都包含了足够的信息来完成其处理， 服务器不需要保存任何客户端的状态信息。

-   **有状态（Statefulset）**

    有状态的系统在处理请求或通信时会记住之前的状态信息。这意味着系统会存储客户端的历史信息 或状态，并基于这些信息进行处理

    有状态应用会在其会话中保存客户端的数据，并且有可能会在客户端下一次的请求中使用这些数据

    应用上常见的状态类型:会话状态、连接状态、配置状态、集群状态、持久性状态等

    典型的有状态系统包括数据库系统、TCP连接等。这些系统需要在通信过程中维护状态信息，以确 保数据的可靠性和一致性。

**无状态和有状态应用区别**

-   **复杂度**：有状态系统通常比无状态系统更复杂，因为它们需要维护和管理状态信息。无状态系统则 更简单，因为它们不需要处理状态信息。
-   **可伸缩性**：无状态系统通常更易于扩展，因为它们不需要考虑会话状态，可以更容易地实现负载均 衡和水平扩展。有状态系统可能需要更复杂的状态管理和同步机制，因此在大规模应用中可能需要 更多的资源和设计考虑。

大型应用通常具有众多功能模块，这些模块通常会被设计为**有状态模块**和**无状态模块**两部分

-   业务逻辑模块一般会被设计为无状态，这些模块需要将其状态数据保存在有状态的中间件服务上， 如消息队列、数据库或缓存系统等
-   无状态的业务逻辑模块易于横向扩展，有状态的后端则存在不同的难题

Http 协议是无状态的，对于http协议本身的每一次请求都是相互独立的，彼此之间没有关联关系。

而 Http 相关的应用往往是有状态的。

很多的 Web 程序是需要有大量的业务逻辑相互关联才可以实现最终的目标，也就是说基于http协议的 web应用程序是有状态的。

只不过这个状态是需要借助于其他的机制来实现，比如 cookies、session、token以及其他辅助的机 制。

为了实现http的会话有状态，基于 cookies、session、token等机制都涉及到文件的保存，要么保存到 客户端，要么保存到服务端。

以session为例，就在服务端保存相关的信息，提高正常通信的效率。

实际的生产环境中，web程序为了保证高可用，所以通过集群的方式实现，应用的访问分布式效果。

在这种场景中，可以基于下面方法实现有状态的会话保持

-   **session sticky** - 根据用户的行为数据，找到上次响应请求的服务器，直接响应
-   **session cluster** - 通过服务集群之间的通信机制实现会话数据的同步
-   **session server** - 借助于一个专用的服务器来保存会话信息。

生产中一些中间件业务集群，比如MySQL集群、Redis集群、ElasticSearch集群、MongoDB集群、 Nacos集群、MinIO集群、Zookeeper集群、Kafka集群、RabbitMQ集群等

这些应用集群都有以下相同特点：

-   每个节点都有固定的身份ID，集群成员通过身份ID进行通信
-   集群的规模是比较固定的，一般不能随意变动
-   节点都是由状态的，而且状态数据通常会做持久化存储
-   集群中某个节点出现故障，集群功能肯定受到影响。

像这种状态类型的服务，只要过程中存在一点问题，那么影响及范围都是不可预测。

**应用编排工作负载型控制器**

-   无状态应用编排:Deployment<--ReplicaSet
-   系统级应用编排:DaemonSet
-   有状态应用编排: StatefulSet
-   作业类应用编排:CronJob <--job

## StatefulSet 工作机制

Pod的管理对象有Deployment，RS、DaemonSet、RC这些都是面向无状态的服务，满足不了上述的有 状态集群的场景需求

从Kubernetes-v1.4版本引入了集群状态管理的功能，v1.5版本更名为StatefulSet 有状态应用副本集

StatefulSet 最早在 Kubernetes 1.5 版本中引入，作为一个 alpha 特性。经过几个版本的改进和稳定， 在 Kubernetes 1.9 版本中，StatefulSet 变成了一个稳定的、通用可用（GA，General Availability）的 特性。

StatefulSet 旨在与有状态的应用及分布式系统一起使用。然而在 Kubernetes 上管理有状态应用和分布 式系统是一个宽泛而复杂的话题。

由于每个有状态服务的特点，工作机制和配置方式都存在很大的不同，因此当前Kubernetes并没有提供 统一的具体的解决方案

```
而 Statefulset 只是为有状态应用提供了基础框架，而非完整的解决方案
如果想实现具体的有状态应用，建议可以使用相应的专用 Operator 实现
```



###### StatefulSet 特点



-   每个Pod 都有稳定、唯一的网络访问标识
-   每个**Pod 彼此间的通信基于Headless Service实现**
-   StatefulSet 控制的Pod副本启动、扩展、删除、更新等操作都是有顺序的
-   StatefulSet里的每个Pod存储的数据不同，所以采用专用的稳定独立的持久化存储卷，用于存储 Pod的状态数据

StatefulSet 对应Pod 的网络标识

-   每个StatefulSet对象对应于一个专用的Headless Service 对象
-   使用 Headless service 给每一个StatufulSet控制的Pod提供一个唯一的DNS域名来作为每个成员的 网络标识
-   每个Pod都一个从0开始，从小到的序号的名称，创建和扩容时序号从小到大，删除，缩容和更新 镜像时从大到小
-   通过ClusterDNS解析为Pod的地址，从而实现集群内部成员之间使用域名通信

每个Pod对应的DNS域名格式：

```
$(statefulset_name)-$(orederID).$(headless_service_name).$(namespace_name).svc.cluster.local
 
#示例
mysql-0.mysql.wordpress.svc.cluster.local
mysql-1.mysql.wordpress.svc.cluster.local
mysql-2.mysql.wordpress.svc.cluster.local
```

定义创建、删除及扩缩容等管理操作期间，在Pod副本上的创建两种模式

-   **OrderedReady**

    创建或扩容时，**顺次**完成各Pod副本的创建，且要求只有前一个Pod转为Ready状态后，才能进行后一个Pod副本的创建

    删除或缩容时，逆序、依次完成相关Pod副本的终止

-   **Parallel**

    各Pod副本的创建或删除操作不存在顺序方面的要求，可同时进行

## StatefulSet 的存储方式



-   基于podTempiate定义Pod模板
-   在`podTemplate`上使用`volumeTemplate`为各Pod副本动态置备`PersistentVolume`
-   因为每个Pod存储的状态数据不尽相同，所以在创建每一个Pod副本时绑定至专有的固定的PVC
-   **PVC的名称遵循特定的格式，从而能够与StatefulSet控制器对象的Pod副本建立紧密的关联关系**
-   支持从静态置备或动态置备的PV中完成绑定
-   删除Pod(例如缩容)，并不会一并删除相关的PVC

## StatefulSet 组件

| 组件                | 描述                                                         |
| ------------------- | ------------------------------------------------------------ |
| headless service    | 一般的Pod名称是随机的，而为了statefulset的唯一性，所以借用 headless service通过唯一的"网络标识"来直接指定的pod应用，所以它要求我们的**dns环境**是完好的。 当一个StatefulSet挂掉，新创建的StatefulSet会被赋予跟原来的Pod 一样的名字，通过这个名字来匹配到原来的存储，实现了状态保存。 |
| volumeClaimTemplate | 有状态集群中的副本数据是不一样的(例：redis)，如果用共享存储的 话，会导致多副本间的数据被覆盖，为了statefulsed数据持久化，需要将pod和其申请的数据卷隔离开，**每一种pod都有其独立的对应的数据卷配置模板**，来满足该要求。 |

## StatefulSet 局限性

根据对 StatefulSet的原理解析，如果实现一个通用的有状态应用的集群，那基本没有可能完成

原因是不同的应用集群，其内部的状态机制几乎是完全不同的

| 集群           | 解析                                                         |
| -------------- | ------------------------------------------------------------ |
| MySQL 主从集群 | 当向当前数据库集群添加从角色节点的时候，可不仅仅为添加一个唯一的节点标识及对 应的后端存储就完了。我们要提前知道，从角色节点的时间、数据复制的起始位置(日志文件名、日志位置、时间戳等)，然后才可以进行数据的同步。 |
| Redis 主从集群 | 集群中，添加节点的时候，会自动根据slaveof设定的主角色节点上获取最新的数据， 然后直接在本地还原，然后借助于软件专用的机制进行数据的同步机制。 |

-   StatefulSet本身的代码无法考虑周全到所有的集群状态机制
-   StatefulSet 只是提供了一个基础的编排框架
-   有状态应用所需要的管理操作，需要由用户自行编写代码完成

这也是为什么早期的Kubernetes只能运行无状态的应用，为了实现所谓的状态集群效果，只能将所有的 有状态服务独立管理，然后以自建EndPoint或者ExternalName的方式引入到Kubernetes集群中，实现 所谓的类似状态效果.

当前而这种方法仍然在很多企业中使用。

# StatefulSet 配置

注意：StatefulSet除了需要定义自身的标签选择器和Pod模板等属性字段，StatefulSet必须要配置一个专用的Headless Service，而且还可能要根据需要，编写代码完成扩容、缩容等功能所依赖的必要操作步骤

**属性解析**

```yaml
apiVersion: apps/v1                    # API群组及版本
kind: StatefulSet                      # 资源类型的特有标识
metadata:             
  name: <string>                       # 资源名称，在作用域中要唯一
  namespace: <string>                  # 名称空间：Statefulset隶属名称空间级别
spec:
  replicas: <integer>                  # 期望的pod副本数，默认为1
  selector: <object>                   # 标签选择器，须匹配pod模版中的标签，必选字段
  template: <object>                   # pod模版对象，必选字段
  revisionHistoryLimit: <integer>      # 滚动更新历史记录数量，默认为10
  updateStragegy: <Object>             # 滚动更新策略
    type: <string>                     # 指定更新策略类型，可用值：OnDelete和Rollingupdate
                                       # OnDelete 表示只有在手动删除旧 Pod 后才会触发更新
                                       # RollingUpdate 表示会自动进行滚动更新
    rollingUpdate: <Object>            # 滚动更新参数，专用于RollingUpdate类型
      maxUnavailable: <integer>        # 更新期间可比期望的Pod数量缺少的数量或比例
      partition: <integer>             # 分区值，表示只更新大于等于此索引值的Pod，默认为0,一般用于金丝雀场景，更新和                                              缩容时都是索引号的Pod从大到小进行，即按从大到小的顺序进行，比如：                                                       MySQL2,MySQL-1,MySQL-0
  serviceName: <string>                # 相关的Headless Service的名称，必选字段
    apiVersion: <string>               # PVC资源所属的API群组及版本，可省略
    kind: <string>                     # PVC资源类型标识，可省略
    metadata: <Object>                 # 卷申请模板元数据
    spec: <Object>                     # 期望的状态，可用字段同PVC
  podManagementPolicy: <string>        # Pod管理策略，默认“OrderedReady”表示顺序创建并逆序删除，“Parallel”表示并                                              行模式
  volumeClaimTemplates: <[]Object>     # 指定PVC的模板.存储卷申请模板，实现数据持久化
  - metadata:
    name: <string>                     # 生成的PVC的名称格式为：<volumeClaimTemplates>. <StatefulSet>-<orederID>
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "sc-nfs"       #  如果有动态置备的StorageClass,可以指定名称
      resources:
        requests:
          storage: 1Gi
```

## StatefulSet 更新策略

更新策略可以实现滚动更新发布

```
  updateStrategy: <Object>         # 滚动策略
    type: <string>                 # 滚动更新类型，可用值有OnDelete和RollingUpdate
    rollingUpdate: <Object>        # 滚动更新参数，专用于RollingUpdate类型
      partition: <integer>         # 分区指示索引值，默认为0,一般用于版本分区域更新场景
```

**快速对比表**：

| 类型            | 含义                                        | 是否自动更新 Pod     | 使用场景                                 | 是否常用 |
| --------------- | ------------------------------------------- | -------------------- | ---------------------------------------- | -------- |
| `RollingUpdate` | 自动按顺序滚动更新 StatefulSet 中的 Pod     | ✅ 是                 | 版本更新、无状态或轻微有状态的服务       | 常用     |
| `OnDelete`      | 仅当手动删除 Pod 后，才会用新的版本重新创建 | ❌ 否（需手动删 Pod） | 对升级控制要求严格的数据库、中间件等场景 | 次常用   |

**结合 `rollingUpdate.partition` 使用（灰度升级）**

```
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    partition: 1
```

表示只有 `ordinal >= 1` 的 Pod 会被更新，比如：

-   `pod-1`, `pod-2` 会更新
-   `pod-0` 保持原样

🎯 用于灰度或分批升级，比如先升级从节点，最后升级主节点。

## 缩容和扩容

缩容和扩容都是按一定的顺序进行的

扩容是从编号为0到N的顺序创建Pod

缩容正好相反, 是从编号N到0的顺序销毁Pod

```
# 缩容，从大到小删除
[root@master1 /]#kubectl scale sts myapp --replicas=1; kubectl get pod -w
statefulset.apps/myapp scaled
NAME                        READY   STATUS        RESTARTS      AGE
myapp-0                     1/1     Running       0             30m
myapp-1                     1/1     Running       0             29m
myapp-2                     1/1     Terminating   0             29m
myapp-2                     0/1     Terminating   0             29m
myapp-1                     1/1     Terminating   0             30m
myapp-1                     0/1     Terminating   0             30m

[root@master1 /]#kubectl get pvc
NAME                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
myappdata-myapp-0   Bound    pvc-4affd28a-5835-4018-bb49-ad07f19b89c4   1Gi        RWO            sc-nfs         <unset>                 32m
myappdata-myapp-1   Bound    pvc-d617b16a-112c-4355-b88f-d81bb699c2a7   1Gi        RWO            sc-nfs         <unset>                 31m
myappdata-myapp-2   Bound    pvc-357b644a-5de5-4889-a9cb-40250d89d6f3   1Gi        RWO            sc-nfs         <unset>                 31m

# 可以看到：pod的删除不影响pv和pvc，说明pod的状态数据没有丢失，而且pvc指定的名称不变，只要是同一个statufulset创建的pod，会自动找到根据指定的pvc找到具体的pv
# pvc 的名称是 <PVC_name>-<POD_name>的组合，所以pod可以直接找到绑定的pvc

# 扩容，从小到大创建pod
[root@master1 /]#kubectl scale sts myapp --replicas=4; kubectl get pod -w
statefulset.apps/myapp scaled
NAME                        READY   STATUS              RESTARTS      AGE 
myapp-0                     1/1     Running             0             33m
myapp-1                     0/1     ContainerCreating   0             1s
myapp-1                     0/1     ContainerCreating   0             3s
myapp-1                     1/1     Running             0             5s
myapp-2                     0/1     Pending             0             0s
myapp-2                     0/1     Pending             0             0s
myapp-2                     0/1     ContainerCreating   0             0s
myapp-2                     0/1     ContainerCreating   0             2s
myapp-2                     1/1     Running             0             4s
myapp-3                     0/1     Pending             0             0s
myapp-3                     0/1     Pending             0             0s
myapp-3                     0/1     Pending             0             2s
myapp-3                     0/1     ContainerCreating   0             2s
myapp-3                     0/1     ContainerCreating   0             4s
myapp-3                     1/1     Running             0             6s

# 只要是同一个statufulset创建的pod，会自动找到根据指定的pvc找到具体的pv
[root@master1 /]#curl 192.168.253.72
myapp-2
```

# MySQL 主从复制集群

##### 准备 NFS 服务和 StorageClass 动态置备



```
# 详情参考Kubernetes数据存储 -> StorageClass -> NFS StorageClass
# 查看定义好的StorageClass
[root@master1 ~]#kubectl get storageclasses.storage.k8s.io
NAME               PROVISIONER                                   RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
sc-nfs (default)   k8s-sigs.io/nfs-subdir-external-provisioner   Delete          Immediate           false                  40d
```

## 创建 ConfigMap

```
# MySQL的配置
[root@master1 statefulset]#cat sts-mysql-configmap.yaml 
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql
  labels:
    app: mysql
    app.kubernetes.io/name: mysql
data:
  primary.cnf: |
    [mysqld]
    log-bin
  replica.cnf: |
    [mysqld]
    super-read-only
```

## 创建 Service

```
# 为 StatefulSet 成员提供稳定的 DNS 表项的无头服务（Headless Service）
#  主节点的对应的Service

[root@master1 statefulset]#cat sts-mysql-svc.yaml 
apiVersion: v1
kind: Service
metadata:
  name: mysql
  labels:
    app: mysql
    app.kubernetes.io/name: mysql
spec:
  ports:
  - name: mysql
    port: 3306
  clusterIP: None
  selector:
    app: mysql
---
# 用于连接到任一 MySQL 实例执行读操作的客户端服务
# 对于写操作，必须连接到主服务器：mysql-0.mysql
# 从节点的对应的Service，注意：此处无需无头服务（Headless Service）
# 下面的service可以不创建，直接使用无头服务mysql也可以
apiVersion: v1
kind: Service
metadata:
  name: mysql-read
  labels:
    app: mysql
    app.kubernetes.io/name: mysql
    readonly: "true"
spec:
  ports:
  - name: mysql
    port: 3306
  selector:
    app: mysql
```

## 创建 statefulset

```
[root@master1 statefulset]#cat sts-mysql-sts.yaml 
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  selector:
    matchLabels:
      app: mysql
      app.kubernetes.io/name: mysql
  serviceName: mysql
  replicas: 3
  template:
    metadata:
      labels:
        app: mysql
        app.kubernetes.io/name: mysql
    spec:
      initContainers:
      - name: init-mysql
        image: registry.cn-beijing.aliyuncs.com/wangxiaochun/mysql:5.7
        command:
        - bash
        - "-c"
        - |
          # -e: 如果任何命令失败（返回非0），立即退出脚本
          # -x: 输出执行的每一条命令（调试用），可以帮助追踪问题
          # 目的是为了确保脚本执行时透明、可调试，并且失败即停。
          set -ex
          # 基于 Pod 序号生成 MySQL 服务器的 ID。
          [[ $HOSTNAME =~ -([0-9]+)$ ]] || exit 1
          # BASH_REMATCH 是 Bash Shell 的一个内置数组变量，专门用于 正则表达式匹配结果的
          # 当你使用 [[ string =~ regex ]] 这种语法做 正则匹配 时
          # BASH_REMATCH[0] 会包含完整匹配的字符串
          # BASH_REMATCH[1] 开始依次是 每个括号捕获组（capture group）匹配到的内容
          ordinal=${BASH_REMATCH[1]}
          echo [mysqld] > /mnt/conf.d/server-id.cnf
          # 添加偏移量以避免使用 server-id=0 这一保留值。
          echo server-id=$((100 + $ordinal)) >> /mnt/conf.d/server-id.cnf
          # 将合适的 conf.d 文件从 config-map 复制到 emptyDir
          if [[ $ordinal -eq 0 ]]; then
            cp /mnt/config-map/primary.cnf /mnt/conf.d/
          else
            cp /mnt/config-map/replica.cnf /mnt/conf.d/
          fi
        volumeMounts:
        - name: conf
          mountPath: /mnt/conf.d
        - name: config-map
          mountPath: /mnt/config-map
      - name: clone-mysql
        image: registry.cn-beijing.aliyuncs.com/wangxiaochun/xtrabackup:1.0
        command:
        # 副本 Pod 启动时，从前一个副本（ordinal-1）克隆数据库数据，用于初始化数据目录。
        # Pod 是有序启动的（如：mysql-0, mysql-1, mysql-2），且 mysql-1 从 mysql-0 取数据，mysql-2 从 mysql-1 取数据
        - bash
        - "-c"
        - |
          set -ex
          # 如果已有数据，则跳过克隆
          [[ -d /var/lib/mysql/mysql ]] && exit 0
          # 跳过主实例（序号索引0）的克隆
          [[ `hostname` =~ -([0-9]+)$ ]] || exit 1
          ordinal=${BASH_REMATCH[1]}
          [[ $ordinal -eq 0 ]] && exit 0
          # 从原来的对等节点克隆数据
          ncat --recv-only mysql-$(($ordinal-1)).mysql 3307 | xbstream -x -C /var/lib/mysql
          # 准备备份
          xtrabackup --prepare --target-dir=/var/lib/mysql
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
          subPath: mysql
        - name: conf
          mountPath: /etc/mysql/conf.d
      containers:
      - name: mysql
        image: registry.cn-beijing.aliyuncs.com/wangxiaochun/mysql:5.7 
        env:
        - name: MYSQL_ALLOW_EMPTY_PASSWORD
          value: "1"
        ports:
        - name: mysql
          containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
          subPath: mysql
        - name: conf
          mountPath: /etc/mysql/conf.d
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
        livenessProbe:
          exec:
            command: ["mysqladmin", "ping"]
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
        readinessProbe:
          exec:
            # 检查我们是否可以通过 TCP 执行查询（skip-networking 是关闭的）
            command: ["mysql", "-h", "127.0.0.1", "-e", "SELECT 1"]
          initialDelaySeconds: 5
          periodSeconds: 2
          timeoutSeconds: 1
      - name: xtrabackup
        image: registry.cn-beijing.aliyuncs.com/wangxiaochun/xtrabackup:1.0
        ports:
        - name: xtrabackup
          containerPort: 3307
        command:
        - bash
        - "-c"
        - |
          set -ex
          cd /var/lib/mysql

          # 确定克隆数据的 binlog 位置（如果有的话）。
          if [[ -f xtrabackup_slave_info && "x$(<xtrabackup_slave_info)" != "x" ]]; then
            # XtraBackup 已经生成了部分的 “CHANGE MASTER TO” 查询
            # 因为从一个现有副本进行克隆。(需要删除末尾的分号!)
            cat xtrabackup_slave_info | sed -E 's/;$//g' > change_master_to.sql.in
            #  在这里要忽略 xtrabackup_binlog_info （它是没用的）
            rm -f xtrabackup_slave_info xtrabackup_binlog_info
          elif [[ -f xtrabackup_binlog_info ]]; then
            # 直接从主实例进行克隆。解析 binlog 位置
            [[ `cat xtrabackup_binlog_info` =~ ^(.*?)[[:space:]]+(.*?)$ ]] || exit 1
            rm -f xtrabackup_binlog_info xtrabackup_slave_info
            echo "CHANGE MASTER TO MASTER_LOG_FILE='${BASH_REMATCH[1]}',\
                  MASTER_LOG_POS=${BASH_REMATCH[2]}" > change_master_to.sql.in
          fi

          # 检查是否需要通过启动复制来完成克隆
          if [[ -f change_master_to.sql.in ]]; then
            echo "Waiting for mysqld to be ready (accepting connections)"
            until mysql -h 127.0.0.1 -e "SELECT 1"; do sleep 1; done

            echo "Initializing replication from clone position"
            mysql -h 127.0.0.1 \
                  -e "$(<change_master_to.sql.in), \
                          MASTER_HOST='mysql-0.mysql', \
                          MASTER_USER='root', \
                          MASTER_PASSWORD='', \
                          MASTER_CONNECT_RETRY=10; \
                        START SLAVE;" || exit 1
            # 如果容器重新启动，最多尝试一次
            mv change_master_to.sql.in change_master_to.sql.orig
          fi

          # 当对等点请求时，启动服务器发送备份。
          exec ncat --listen --keep-open --send-only --max-conns=1 3307 -c \
            "xtrabackup --backup --slave-info --stream=xbstream --host=127.0.0.1 --user=root"
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
          subPath: mysql
        - name: conf
          mountPath: /etc/mysql/conf.d
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
      volumes:
      - name: conf
        emptyDir: {} 
      - name: config-map
        configMap:
          name: mysql
  volumeClaimTemplates:
  - metadata: 
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "sc-nfs"
      resources:
        requests:
          storage: 10Gi
```

# Operator

由于不同集群的特殊性，所以StatefulSet只能应用于通用的状态管理机制,用户自已实现应用的集群又比较麻烦

一些热心的软件开发者利用Statefulset等技术将应用封装成各种应用程序专用的 Operator，以便于帮助 相关企业进行使用Kubernetes，并将这些做好的状态管理工具放到了 GitHub网站的awsomes operators项目中，当前迁移到了 https://operatorhub.io/

因此如果涉及到一些状态集群场景，建议可以直接使用operatorhub提供好的工具，而无需自己编写实现

## Operator 工作机制

Kubernetes中两个核心的理念：“声明式API”和“控制器模式”。

“声明式API”的核心原理，就是当用户向Kubernetes提交了一个API对象描述之后，Kubernetes会负责为 你保证整个集群里各项资源的状态，都与你的API对象描述的需求保持一致

Kubernetes通过启动一种叫做“控制器模式”的无限循环，watch这些API对象的变化，不断检查，然后调谐，最后确保整个集群的状态与这个API对象的描述一致。

Operator就是基于以上原理工作，以Redis Operator为例，为了实现Operator，首先需要将自定义对 象CRD(Custom Resource Definition)的说明，注册到Kubernetes中，用于描述Operator控制的应用： Redis集群实例，这样当用户告诉Kubernetes想要一个redis集群实例后，Redis Operator就能通过控制 循环执行调谐逻辑达到用户定义状态。

所以**Operator本质上是一个特殊应用的控制器**，其提供了一种在Kubernetes API之上构建应用程序， 并在Kubernetes上部署程序的方法，它允许开发者扩展Kubernetes API，增加新功能，像管理 Kubernetes原生组件一样管理自定义的资源。

如果你想运行一个Redis哨兵模式的主从集群，或者TiDB集群，那么你只需要提交一个声明就可以了， 而不需要关心部署这些分布式的应用需要的相关领域的知识

Operator本身就可以做到创建应用、监控应用状态、扩缩容、升级、故障恢复、及资源清理等，从而将 分布式应用的门槛降到最低。

**基于专用的Operator编排运行某有状态应用的流程：**

-   部署Operator及其专用的资源类型
-   使用上面创建的专用的资源类型，来声明一个有状态应用的编排需求

**Operator 链接：**

```
https://operatorhub.io/
```

# Helm

https://helm.sh/
https://github.com/helm/helm

## Helm 相关概念

-   **Helm**：Helm的客户端工具，负责和API Server 通信

    Helm 和kubectl类似，也是Kubernetes API Server的命令行客户端工具

    支持kubeconfig认证文件

    需要事先从仓库或本地加载到要使用目标Chart，并基于Chart完成应用管理，Chart可缓存于Helm本地主机上 支持仓库管理和包管理的各类常用操作，例如Chart仓库的增、删、改、查，以及Chart包的制作、 发布、搜索、下载等

-   **Chart**：打包文件，将所有相关的资源清单文件YAML的打包文件

    Chart 是一种打包格式，文件后缀为tar.gz或者 tgz，代表着可由Helm管理的有着特定格式的程序包，类似于RPM，DEB包格式

    Chart 包含了应用所需的资源相关的各种yaml/json配置清单文件，比如：deployment,service 等，但不包含容器的镜像

    Chart 可以使用默认配置，或者定制用户自已的配置进行安装应用

    Chart 中的资源配置文件通常以模板(go template)形式定义，在部署时，用户可通过向模板参数赋值实现定制化安装的目的

    Chart 中各模板参数通常也有**默认值**，这些默认值定义在Chart包里一个名为**`values.yml`**的文件中

-   **Release**：表示基于chart部署的一个实例。通过chart部署的应用都会生成一个唯一的Release,即使同一个chart部署多次也会产生多个Release.将这些release应用部署完成后，也会记录部署的一个版本，维护了一个release版本状态,基于此可以实现版本回滚等操作

-   **Repository**：chart包存放的仓库，相当于APT和YUM仓库

## Chart 仓库

**Chart 仓库**：用于实现Chart包的集中存储和分发,类似于Docker仓库Harbor

**Chart 仓库**

-   **官方仓库**: https://artifacthub.io/
-   **微软仓库**: 推荐使用，http://mirror.azure.cn/kubernetes/charts/
-   **阿里云仓库**：http://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts
-   **项目官方仓库**：项目自身维护的Chart仓库
-   **Harbor 仓库**：新版支持基于 **OCI:// 协议**，将Chart 存放在公共的docker 镜像仓库

**Chart 官方仓库Hub:**

```
https://artifacthub.io/
```

## 使用Helm部署应用流程

-   安装 helm 工具

-   查找合适的 chart 仓库

-   配置 chart 仓库

-   定位 chart

-   通过向Chart中模板文件中字串赋值完成其实例化，即模板渲染， 实例化的结果就可以部署到目标 Kubernetes上

    模板字串的定制方式三种：

    -   默认使用 chart 中的 values.yaml 中定义的默认值
    -   直接在helm install的命令行，通过--set选项进行
    -   自定义values.yaml，由helm install -f values.yaml 命令加载该文件

-   同一个chart 可以部署出来的多个不同的实例，每个实例称为一个release

    Chart 和 Release 的关系，相当于OOP开发中的Class和对象的关系,相当于image和container

    应用release 安装命令：helm install

## Helm 客户端安装

https://helm.sh/docs/intro/install/

https://github.com/helm/helm/releases

## Helm 命令用法



```
https://v3.helm.sh/zh/docs/helm/
https://docs.helm.sh/docs/helm/helm/
```

Helm 命令用法说明

**常用的 helm命令分类**

-   **Repostory 管理**

    repo 命令，支持 repository 的`add`、`list`、`remove`、`update` 和 `index` 等子命令

-   **Chart 管理**

    `create`、`package`、`pull`、`push`、`dependency`、`search`、`show` 和 `verify` 等操作

-   **Release 管理**

    `install`、`upgrade`、`get`、`list`、`history`、`status`、`rollback `和 `uninstall` 等操作

**Helm常见子命令**

```
version          # 查看helm客户端版本
repo             # 添加、列出、移除、更新和索引chart仓库，相当于apt/yum仓库,可用子命令:add、index、list、remove、update
search           # 根据关键字搜索chart包
show             # 查看chart包的基本信息和详细信息，可用子命令:all、chart、readme、values
pull             # 从远程仓库中拉取chart包并解压到本地，通过选项 --untar 解压,默认不解压
create           # 创建一个chart包并指定chart包名字
install          # 通过chart包安装一个release实例
list             # 列出release实例名
upgrade          # 更新一个release实例
rollback         # 从之前版本回滚release实例，也可指定要回滚的版本号
uninstall        # 卸载一个release实例
history          # 获取release历史，用法:helm history release实例名
package          # 将chart目录打包成chart存档文件.tgz中
get              # 下载一个release,可用子命令:all、hooks、manifest、notes、values
status           # 显示release实例的状态，显示已命名版本的状态
```

**Helm 常见命令用法**

```
# 仓库管理
helm repo list    # 列出已添加的仓库
helm repo add [REPO_NAME] [URL]  # 添加远程仓库并命名,如下示例
helm repo add myharbor https://harbor.wangxiaochun.com/chartrepo/myweb --username admin --password 123456
helm repo remove [REPO1 [REPO2 ...]]   # 删除仓库
helm repo update                       # 更新仓库,相当于apt update
helm search hub  [KEYWORD]             # 从artifacthub网站搜索,无需配置本地仓库,相当于docker search
helm search repo [KEYWORD]             # 本地仓库搜索,需要配置本地仓库才能搜索,相当于apt search
helm search repo [KEYWORD] --versions  # 显示所有版本
helm show chart [CHART]                # 查看chart包的信息,类似于apt info
helm show values [CHART]               # 查看chart包的values.yaml文件内容

# 拉取chart到本地
helm pull repo/chartname               # 下载charts到当前目录下，表现为tgz文件,默认最新版本，相当于wget  
helm pull chart_URL                    # 直接下载，默认为.tgz文件
helm pull myrepo/myapp --version 1.2.3 --untar      # 直接下载指定版本的chart包并解压缩

# 创建chart目录结构
helm create NAME

# 检查语法
helm lint [PATH]  #默认检查当前目录

# 安装
helm install [NAME] [CHART] [--version <string> ]    # 安装指定版本的chart
helm install [CHART] --generate-name                 # 自动生成  RELEASE_NAME
helm install --set KEY1=VALUE1 --set KEY2=VALUE2  RELEASE_NAME CHART ...    #指定属性实现定制配置
helm install -f values.yaml  RELEASE_NAME CHART..... # 引用文件实现定制配置
helm install --debug --dry-run RELEASE_NAME CHART    # 调试并不执行，可以查看到执行的渲染结果

# 删除
helm uninstall RELEASE_NAME                          # 卸载RELEASE


# 查看
helm list                                            # 列出安装的release
helm status RELEASE_NAME                             # 查看RELEASE的状态
helm get notes RELEASE_NAME -n NAMESPACE             # 查看RELEASE的说明
helm get values RELEASE_NAME -n NAMESPACE > values.yaml   # 查看RELEASE的生成值，可以导出方便以后使用
helm get manifest RELEASE_NAME -n NAMESPACE          # 查看RELEASE的生成的资源清单文件

# 升价和回滚
helm upgrade RELEASE_NAME CHART --set key=newvalue       # release 更新
helm upgrade RELEASE_NAME CHART -f mychart/values.yaml   # release 更新
helm rollback RELEASE_NAME [REVISION]                    # release 回滚到指定版本，如果不指定版本，默认回滚至上一版本
helm history RELEASE_NAME                                # 查看历史

# 打包
helm package mychart/ #将指定目录的chart打包为.tgz到当前目录下
```

## 部署 MySQL

```shell
helm repo add bitnami https://charts.bitnami.com/bitnami

helm repo update 

helm install mysql bitnami/mysql --version 12.3.2 --set primary.persistence.storageClass=openebs-hostpath

helm list 

helm uninstall mysql
```

指定值文件values.yaml内容实现定制Release

```
helm show values bitnami/mysql --version 10.3.0 > value.yaml

helm install mysql bitnami/mysql -f values.yaml
```

MySQL 主从复制

```
helm repo add bitnami https://charts.bitnami.com/bitnami
"bitnami" has been added to your repositories

# 注意：\ 后面不能有任何字符（包括空格、Tab）
[root@master1 ~]# helm install mysql bitnami/mysql  \
    --set 'auth.rootPassword=Zyf646130' \
    --set 'auth.replicationPassword=Zyf646130' \
    --set global.storageClass=sc-nfs \
    --set auth.database=wordpress \
    --set auth.username=wordpress \
    --set 'auth.password=Zyf646130' \
    --set architecture=replication \
    --set secondary.replicaCount=1 \
    -n wordpress --create-namespace
    
# 方法2：通过OCI协议
[root@master1 ~]# helm install mysql  \
    --set auth.rootPassword='P@ssw0rd' \
    --set global.storageClass=sc-nfs \
    --set auth.database=wordpress \
    --set auth.username=wordpress \
    --set auth.password='P@ssw0rd' \
    --set architecture=replication \
    --set secondary.replicaCount=1 \
    --set auth.replicationPassword='P@ssw0rd' \
    oci://registry-1.docker.io/bitnamicharts/mysql \
    -n wordpress --create-namespace
```



主从复制更新副本数为2

```
[root@master1 ~]# helm upgrade mysql \
    --set auth.rootPassword='Zyf646130' \
    --set global.storageClass=sc-nfs \
    --set auth.database=wordpress \
    --set auth.username=wordpress \
    --set auth.password='Zyf646130' \
    --set architecture=replication \
    --set secondary.replicaCount=2 \
    --set auth.replicationPassword='Zyf646130' \
    bitnami/mysql \
    -n wordpress
    
# 查看
[root@master1 ~]# kubectl get pod -n wordpress 
NAME                READY   STATUS     RESTARTS   AGE
mysql-primary-0     1/1     Running    0          7m7s
mysql-secondary-0   1/1     Running    0          7m7s
mysql-secondary-1   0/1     Init:0/1   0          6s

# 三分钟，有点慢
[root@master1 ~]# kubectl get pod -n wordpress 
NAME                READY   STATUS    RESTARTS   AGE
mysql-primary-0     1/1     Running   0          10m
mysql-secondary-0   1/1     Running   0          10m
mysql-secondary-1   1/1     Running   0          3m30s
```

## 部署 WordPress

```
helm install wordpress \
    --version 22.4.20 \
    --set mariadb.enabled=false \
    --set externalDatabase.host=mysql-primary.wordpress.svc.cluster.local \
    --set externalDatabase.user=wordpress \
    --set externalDatabase.password='Zyf646130' \
    --set externalDatabase.port=3306 \
    --set wordpressUsername=admin \
    --set wordpressPassword='Zyf646130' \
    --set persistence.storageClass=sc-nfs \
    --set ingress.enabled=true \
    --set ingress.ingressClassName=nginx \
    --set ingress.hostname=wordpress.mystical.org \
    --set ingress.pathType=Prefix \
    --set externalDatabase.database=wordpress \
    --set volumePermissions.enabled=true \
    --set livenessProbe.enabled=false \
    --set readinessProbe.enabled=false \
    --set startupProbe.enabled=false \
    bitnami/wordpress \
    -n wordpress --create-namespace
    
# 全过程：15分钟左右，其中数据下载：10分钟左右
# NFS上的wordpress数据大小
```

## 部署 Harbor

```
helm repo add harbor https://helm.goharbor.io

helm show values bitnami/harbor > harbor.values.yaml

helm install myharbor -f harbor.values.yaml harbor/harbor -n harbor --create-namespace
```

