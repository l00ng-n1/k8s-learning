# Pod 资源

## 什么是 Pod

Pod 是 Kubernetes API 中最常见最核心资源类型

**Pod 是一个或多个容器的集合**，因而也可称为容器集，但却是Kubernetes调度、部署和运行应用的原子单元

-   同一Pod内的所有容器都将运行于由Scheduler选定的同一个worker节点上
-   在同一个pod内的容器共享的**存储资源**、**网络协议栈**及容器的**运行控制策略**等
-   每个Pod中的容器依赖于一个特殊名为**pause容器**事先创建出可被各应用容器共享的**基础环境**，包括 Network、IPC和UTS名称空间共享给Pod中各个容器，PID名称空间也可以共享，但需要用户显式定 义,**Mount和User是不共享的**,每个容器有独立的Mount,User的名称空间

![image-20250324085941343](pic/image-20250324085941343.png)

od的组成形式有两种

-   **单容器Pod**：除Pause容器外,仅含有一个容器
-   **多容器Pod**：除Pause容器外，含有多个具有“超亲密”关系的容器，一般由主容器和辅助容器（比 如：**sidecar容器**）构成

**Pod资源分类**

-   自主式 Pod
    -   由用户直接定义并提交给API Server创建的Pods
-   由Workload Controller管控的 Pod
    -   比如: 由Deployment控制器管理的Pod
-   静态 Pod
    -   由kubelet加载配置信息后，自动在对应的节点上创建的Pod
    -   用于实现Master节点上的系统组件API Server 、Controller-Manager 、Scheduler 和Etcd功能的 Pod
    -   相关配置存放在控制节点的 **`/etc/kubernetes/manifests`** 目录下

**总结：**

-   Pod中最少有2个容器
-   Pod = **Pause容器** + 业务容器

### 静态pod

```shell
# 静态pod创建流程
/etc/kubernetes/manifests目录下yaml文件 ---> kubelet --> docker runc --> ETCD | ApiServer Pod ...

ls /etc/kubernetes/manifests/
etcd.yaml  kube-apiserver.yaml  kube-controller-manager.yaml  kube-scheduler.yaml

# 将资源清单文件放入/etc/kubernetes/manifests/中，会被kubelet自动拉起
```

### 自主式Pod

```shell
# 自定义pod创建流程
kuebctl --> apiserver --> kubelet --> docker runc --> pod容器
```

通过kubectl 命令行工具指定选项创建 Pod，适合**临时性**工作

```shell
kubectl run NAME --image=image [--port=port] [--replicas=replicas] 

kubectl run NAME --image=image [--env="key=value"] [--port=port] [--dry-run=server|client] [--overrides=inline-json] [--command] -- [COMMAND] [args...] [options]

#参数详解
--image=''       #指定容器要运行的镜像
--port=''        #设定容器暴露的端口
--dry-run=true   #以模拟的方式来进行执行命令
--env=[]         #执行的时候，向对象中传入一些变量
--labels=''      #设定pod对象的标签
--limits='cpu=200m,memory=512Mi' #设定容器启动后的资源配置
--replicas=n     #设定pod的副本数量,新版不再支持
--command=false     #设为true，将 -- 后面的字符串做为命令代替容器默认的启动命令，而非做为默认启动命令的参数
-it              #打开交互终端
--rm             #即出即删除容器
--restart=Never  #不会重启
```

示例

```shell
kubectl run myapp-pod --image=harbor.l00n9.icu/public/myapp:v1.0

# 创建Busybox的Pod,默认busybox没有前台进程,需要指定前台程序才能持继运行
kubectl run busybox --image harbor.l00n9.icu/public/busybox:unstable-uclibc -- sleep 3600
# 传参
kubectl run busybox --image busybox:1.30 --env="NAME=test" -- sleep 3600

# 进入容器
kubectl exec -it busybox -- sh
/ # echo $NAME
test
```

## pod资源清单范例

### yaml格式的Pod清单文件-极简版

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: busybox
  namespace: m61-namespace
spec:
  containers:
  - image: harbor.l00n9.icu/public/busybox:unstable-uclibc
    name: busybox
```

### yaml格式的Pod清单文件实例-完整版

```shell
# yaml格式的Pod定义文件完整内容
apiVersion: v1
kind: Pod
metadata:
  name: string
  namespace: string
  labels:
    name: string
  annotations:
    name: string
spec:
  initContainers:
  - name: string
    image: string
    imagePullPolicy: Always  # Options: Always, Never, IfNotPresent
    command: 
      - string
    args: 
      - string
  containers:
  - name: string
    image: string
    imagePullPolicy: Always  # Options: Always, Never, IfNotPresent
    command: 
      - string
    args: 
      - string
    workingDir: string
    volumeMounts:
    - name: string
      mountPath: string
      readOnly: true  # Options: true, false
    ports:
    - name: string
      containerPort: 80  # Replace with the correct port
      hostPort: 80  # Replace with the correct port
      protocol: TCP  # Options: TCP, UDP, SCTP
    env:
    - name: string
      value: string
    resources:
      limits:
        cpu: "500m"  # Replace with actual limit
        memory: "128Mi"  # Replace with actual limit
      requests:
        cpu: "250m"  # Replace with actual request
        memory: "64Mi"  # Replace with actual request
    startupProbe:
      httpGet:
        path: /healthz
        port: 80  # Replace with actual port
    livenessProbe:
      exec:
        command: 
          - string
      httpGet:
        path: /healthz
        port: 80  # Replace with actual port
        host: localhost  # Replace with actual host
        scheme: HTTP  # Options: HTTP, HTTPS
        httpHeaders:
        - name: string
          value: string
      tcpSocket:
        port: 80  # Replace with actual port
      initialDelaySeconds: 10
      timeoutSeconds: 5
      periodSeconds: 10
      successThreshold: 1
      failureThreshold: 3
    securityContext:
      privileged: false  # Options: true, false
  restartPolicy: Always  # Options: Always, Never, OnFailure
  nodeSelector: 
    disktype: ssd  # Example node selector
  nodeName: string  # Replace with actual node name
  imagePullSecrets:
  - name: my-secret  # Replace with actual secret name
  hostNetwork: false  # Options: true, false
  volumes: 
  - name: empty-volume
    emptyDir: {}
  - name: host-path-volume
    hostPath:
      path: /data/volume  # Replace with actual path
  - name: secret-volume
    secret:
      secretName: string  # Replace with actual secret name
      items:     
      - key: string
        path: string
  - name: configmap-volume
    configMap:
      name: string  # Replace with actual ConfigMap name
      items:
      - key: string
        path: string
```

## pod管理命令

```yaml
vim pod-nginx.yaml

apiVersion: v1
kind: Pod
metadata:
  name: pod-nginx1
  namespace: default
spec:
  containers:
  - name: nginx-web01
    image: harbor.l00n9.icu/public/nginx:stable-perl  
```

### 创建 Pod 资源

```shell
kubectl apply -f pod-nginx.yaml
kubectl create -f pod-nginx.yaml

kubectl get pods -o wide

kubectl describe pod pod-nginx1
```

### 更新Pod资源

```shell
# 导出pod的资源清单
kubectl get pods pod-nginx1 -o yaml > pod-1-update.yaml

# 编辑镜像版本
vim pod-test1-update.yaml

# 更新
kubectl replace -f pod-test1-update.yaml
# replace不建议使用，没有幂等性，建议apply

```

### 查看 Pod 状态

```shell
kubectl get pod <pod_name> [(-o|--output=)json|yaml|jsonpath] [-n namespace]
kubectl describe pod <pod_name> [-n namespace]
```

```shell
kubectl get pods pod-nginx1 -o wide
NAME         READY   STATUS    RESTARTS   AGE    IP           NODE              NOMINATED NODE   READINESS GATES
pod-nginx1   1/1     Running   0          117s   10.244.2.6   node2.l00n9.icu   <none>           <none>

kubectl describe pod pod-nginx1
...
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  39s   default-scheduler  Successfully assigned default/pod-nginx1 to node2.l00n9.icu
  Normal  Pulled     39s   kubelet            Container image "harbor.l00n9.icu/public/nginx:stable-perl" already present on machine
  Normal  Created    39s   kubelet            Created container: nginx-web01
  Normal  Started    39s   kubelet            Started container nginx-web01
```

### 查看Pod中指定容器应用的日志

```shell
kubectl logs [-f] (POD | TYPE/NAME) [-c CONTAINER] [options]

# 选项
-p 前一个已退出的容器的日志
--all-containers=true 所有容器
--tail=N 最后N个日志
```

```shell
kubectl logs pod-nginx1 
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2025/03/24 03:03:07 [notice] 1#1: using the "epoll" event method
2025/03/24 03:03:07 [notice] 1#1: nginx/1.26.3
2025/03/24 03:03:07 [notice] 1#1: built by gcc 12.2.0 (Debian 12.2.0-14) 
2025/03/24 03:03:07 [notice] 1#1: OS: Linux 5.15.0-134-generic
2025/03/24 03:03:07 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2025/03/24 03:03:07 [notice] 1#1: start worker processes
2025/03/24 03:03:07 [notice] 1#1: start worker process 29
2025/03/24 03:03:07 [notice] 1#1: start worker process 30
```

### 进入Pod 执行命令

```shell
kubectl exec (POD | TYPE/NAME) [-c CONTAINER] [flags] -- COMMAND [args...] [options]
```

```shell
# -it 分配伪终端
kubectl exec -it pod-nginx1 -- sh

kubectl exec -it pod-nginx1 -- bash
```

### 删除 Pod

```shell
kubectl delete pod <pod_name> ... [--force --grace-period=0]
```

```shell
#优雅删除
kubectl delete pod pod-nginx1

#强制删除，宽限期为0s
kubectl delete pod pod-nginx1 --force --grace-period=0

# 根据资源清单删除
kubectl delete -f pod-nginx.yaml
```

## 创建定制的Pod

kubernets 支持多种定制 Pod 的实现方法

-   对于不同应用的Pod,重新定制对应的镜像（重打镜像，最拉）
-   启动容器时指定env环境变量
-   启动容器的指定command和args
-   将配置信息基于卷资源对象，再将其加载到容器，比如：configMap和secret等

### 利用环境变量`env`实现容器传参

mysql

```yaml
vim pod-mysql.yml
apiVersion: v1
kind: Pod
metadata:
  name: mydb
  namespace: default
spec:
  containers:
  - name: mysql
    image: harbor.l00n9.icu/public/mysql:8.0.41-debian
    env:
    - name: MYSQL_ROOT_PASSWORD
      value: "123456"
    - name: MYSQL_DATABASE
      value: wordpress
    - name: MYSQL_USER
      value: wpuser
    - name: MYSQL_PASSWORD
      value: "123456"
```

```shell
kubectl apply -f pod-mysql.yaml

kubectl get pods mydb -o wide
NAME   READY   STATUS    RESTARTS   AGE   IP           NODE              NOMINATED NODE   READINESS GATES
mydb   1/1     Running   0          29s   10.244.1.3   node1.l00n9.icu   <none>           <none>

kubectl describe pod mydb
Containers:
...
    Environment:
      MYSQL_ROOT_PASSWORD:  123456
      MYSQL_DATABASE:       wordpress
      MYSQL_USER:           wpuser
      MYSQL_PASSWORD:       123456
```

wordpress

```shell
vim pod-wordpress.yaml
apiVersion: v1
kind: Pod
metadata:
  name: wordpress
  namespace: default
spec:
  containers:
  - name: wordpress
    image: harbor.l00n9.icu/public/wordpress:php8.1-apache
    env:
    - name: WORDPRESS_DB_HOST
      value: 10.244.1.3
    - name: WORDPRESS_DB_NAME
      value: wordpress
    - name: WORDPRESS_DB_USER
      value: wpuser
    - name: WORDPRESS_DB_PASSWORD
      value: "123456"
```

```shell
kubectl apply -f pod-wordpress.yaml

kubectl get pods -o wide

kubectl describe pod wordpress
```

### 利用`command`和`args`字段传递容器的启动命令和参数

Pod配置中，spec.containers[].command字段能够在容器上指定替代镜像默认运行的应用程序，且可 同时使用spec.containers[].args字段进行参数传递，它们将覆盖镜像中的默认定义的参数。

-   若仅定义了command字段时，其值将覆盖镜像中定义的程序及参数。
-   若仅是定义了args字段，该字段值将作为参数传递给镜像中默认指定运行的应用程序
-   **注意: args中使用环境变量,需要使用格式: $(环境变量名)**

```yaml
vim pod-with-cmd-and-args.yaml 
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-cmd-and-args
spec:
  containers:
  - name: pod-test
    image: harbor.l00n9.icu/public/pod-test:v0.1
    command: ['/bin/sh','-c']
    # args: ['python3 /usr/local/bin/demo.py -p 8080']
    args: ['python3 /usr/local/bin/demo.py -p $(port)']
    env:
    - name: port
      value: "8888"
```

```shell
kubectl apply -f pod-with-cmd-and-args.yaml

kubectl get pod -o wide

kubectl exec  pod-with-cmd-and-args  -- ps aux
```

## 容器的外部访问

### 使用宿主机网络实现容器的外部访问

默认容器使用私有的独立网段，无法从集群外直接访问，可以通过下面两种方式实现外部访问

-   让容器直接使用宿主机的网络地址，即容器使用host的网路模型
-   让容器通过宿主机的端口映射实现，即DNAT

**注意：都要避免端口冲突**

使用宿主机网络

```yaml
Vim pod-hostnetwork.yaml 
apiVersion: v1
kind: Pod
metadata:
  name: pod-hostnetwork-demo
spec:
  hostNetwork: true
  containers:
  - name: demo-env
    image: harbor.l00n9.icu/public/pod-test:v0.1
    env:
    - name: PORT
      value: "9999"
```

端口映射到宿主机端口

```yaml
cat pod-hostport.yaml 
apiVersion: v1
kind: Pod
metadata:
  name: pod-hostport-demo
spec:
  containers:
  - name: demo-env
    image: harbor.l00n9.icu/public/pod-test:v0.1
    env:
    - name: PORT
      value: "9999"
    ports:                           # 使用宿主机指定端口
    - name: http                     # 不支持大写字母
      containerPort: 9999            # 使用上面变量相同的端口
      hostPort: 8888
      
# 本质上就是通过宿主机的DNAT策略实现
# ss -tnulp是看不见的
iptables -vnL -t nat |grep DNAT
```

### 定义service资源

给容器做外部访问的代理

可实现负载均衡

用 NodePort 或 Ingress 暴露 WordPress

```yaml
vim pod-service.yaml
---
apiVersion: v1
kind: Pod
metadata:
  name: mydb
  namespace: default
  labels:
    app: mysql
spec:
  containers:
  - name: mysql
    image: harbor.l00n9.icu/public/mysql:8.0.41-debian
    env:
    - name: MYSQL_ROOT_PASSWORD
      value: "123456"
    - name: MYSQL_DATABASE
      value: wordpress
    - name: MYSQL_USER
      value: wpuser
    - name: MYSQL_PASSWORD
      value: "123456"
      
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: mysql
  name: mysql
spec:
  ports:
  - name: 3306-3306
    port: 3306
    protocol: TCP
    targetPort: 3306
  selector:
    app: mysql
  type: ClusterIP

---      
apiVersion: v1
kind: Pod
metadata:
  name: wordpress
  namespace: default
  labels:
    app: wp
spec:
  containers:
  - name: wordpress
    image: harbor.l00n9.icu/public/wordpress:php8.1-apache
    env:
    - name: WORDPRESS_DB_HOST
      value: mysql
    - name: WORDPRESS_DB_NAME
      value: wordpress
    - name: WORDPRESS_DB_USER
      value: wpuser
    - name: WORDPRESS_DB_PASSWORD
      value: "123456"
      
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: wp
  name: wp
spec:
  ports:
  - name: 80-80
    port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: wp
  type: NodePort
```

```shell
kubectl get pods,svc -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP            NODE              NOMINATED NODE   READINESS GATES
pod/mydb                    1/1     Running   0          10s   10.244.1.12   node1.l00n9.icu   <none>           <none>
pod/pod-with-cmd-and-args   1/1     Running   0          98s   10.244.1.11   node1.l00n9.icu   <none>           <none>
pod/wordpress               1/1     Running   0          10s   10.244.2.11   node2.l00n9.icu   <none>           <none>

NAME                 TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE     SELECTOR
service/kubernetes   ClusterIP   10.96.0.1       <none>        443/TCP        3d21h   <none>
service/mysql        ClusterIP   10.108.129.64   <none>        3306/TCP       10s     app=mysql
service/wp           NodePort    10.100.78.44    <none>        80:32178/TCP   10s     app=wp
```

`curl 10.0.0.104:32178`

## 临时容器

有时有必要检查现有 Pod 的状态。例如，对于难以复现的故障进行排查。 在这些场景中，可以在现有 Pod 中运行临时容器来检查其状态并运行任意命令。

Kubernetes v1.16推出临时容器, Kubernetes v1.25稳定可用, 就是在原有的Pod 上，添加一个**临时的 Container，这个Container可以包含我们排查问题所有的工具**, 比如: ip、ss、ps、pstree、top、kill、 top、jstat、jmap等

*   **临时创建一个调试容器（Pod）**，
*    **在已存在 Pod 上挂载一个 debug 容器（类似 sidecar）**，
*    **进入容器排查问题**（比 `kubectl exec` 更灵活），

*   **用于网络、镜像、权限、存储等疑难问题排查**

###  附加调试容器到已存在的 Pod（非破坏式）

```shell
kubectl debug <pod-name> -c <container-name> --image=busybox --target=<container-name> --copy-to=debug-<pod-name>


kubectl debug wordpress -c wordpress --image=busybox --target=wordpress --copy-to=debug-wordpress
```

创建一个副本 `debug-wordpress`

复制了原容器的配置

用 `busybox` 替换主镜像（可用于排查镜像无法启动等问题）

可以加上 `--share-processes`、`--share-network` 来共享进程空间或网络

### 在原 Pod 上临时挂载调试容器（类似 sidecar）【K8s v1.18+】

```
kubectl debug <pod-name> -it --image=nicolaka/netshoot --share-processes -- bash
```

使用 `netshoot` 镜像（内置很多网络工具）

和目标 Pod 共用 PID、Network、IPC 空间

可以直接查看目标容器的网络状态、进程、配置等

# Pod 工作机制

![image-20250324171411285](pic/image-20250324171411285.png)

## Pause容器

Pause容器 全称 infrastucture container（又叫infra）基础容器

-   **pause 容器** 是每个 Pod 中的一个“基础”或“辅助”容器，作为 **“Pod的基础环境”**。
-   pause 容器的核心目的是：
    1.  作为 Pod 中所有其他容器的“**根命名空间**”（包括网络、PID、IPC、用户命名空间等）。
    2.  提供一个**管理所有容器的父容器**。
    3.  充当**网络栈的宿主**，即将 Pod 的 IP 地址分配到 pause 容器。
    4.  **防止孤儿进程**：pause 容器负责回收 Pod 中子进程（即僵尸进程），防止孤儿进程残留。
    5.  **统一管理生命周期**：当 Pod 被销毁时，**所有与 pause 容器共享命名空间的容器**也会被销毁。

| **作用**          | **描述**                                                     |
| ----------------- | ------------------------------------------------------------ |
| **网络命名空间**  | Pod 中的网络栈是 pause 容器的网络栈，所有其他容器与它共享 IP 地址、端口和网络命名空间。 |
| **PID 命名空间**  | Pod 内的所有容器与 pause 容器共享一个 PID 命名空间，Pod 内的进程能“看到”彼此的进程列表。 |
| **IPC 命名空间**  | 容器之间的进程通信（如信号、信号量）是通过 IPC 实现的，Pod 中的 IPC 命名空间由 pause 容器提供。 |
| **Volume 卷管理** | 如果 Pod 中有挂载卷，卷的路径通常先挂载到 pause 容器的文件系统中，其他容器共享这个路径。 |
| **僵尸进程回收**  | 如果 Pod 内的某个容器内的子进程退出，这个僵尸进程不会直接被宿主机的 init 进程 (PID 1) 回收，而是由 pause 容器回收。 |
| **父进程作用**    | pause 容器的 PID 始终是 Pod 中的第一个进程 (PID=1)，所有其他进程（即业务容器的进程）都是 pause 容器的“子进程”。 |

-    当 kubelet 启动一个 Pod 时：
    -   **pause 容器首先启动**，这是 Pod 的第一个容器。
    -   启动 pause 容器的原因是：它会创建**PID 命名空间、网络命名空间、IPC 命名空间和 UTS 命名空间**。
    -   pause 容器的 PID 在 Pod 命名空间中是 **1**，即**PID=1**。
-    当其他业务容器启动时：
    -   业务容器不会从 pause 容器 fork() 出来，而是**containerd 或 dockerd** 启动的。
    -   业务容器和 pause 容器**共享 pause 容器的命名空间**（网络、IPC、PID、Volume 等），这就是“共享”命名空间的含义。
    -   **从 PID 视角看**，所有业务容器中的进程都属于 pause 容器的子进程。

**为什么需要 pause 容器？**

-   统一命名空间：
    -   Pod 中的多个业务容器共享**网络命名空间**，这使得它们共享一个 IP 地址（Pod IP）。
    -   通过 pause 容器的 PID 1，所有业务容器可以共享同一个 PID 命名空间。
-   负责回收子进程：
    -   **回收僵尸进程**：如果业务容器内部的进程 (PID) 终止，会成为僵尸进程，系统的 init 进程通常负责回收僵尸进程。
    -   在 Pod 中，**pause 容器就是 Pod 中的 "init 进程"**，负责回收业务容器中的僵尸进程。
-   网络栈的基础：
    -   通过 pause 容器的网络命名空间，Pod 中的每个业务容器共享一个 IP 地址和端口空间。

## pod通信机制

-   Pod内多容器通信：容器件通信（容器模型）借助于pause容器实现
-   单节点内多Pod通信：主机间容器通信（host模型），利用kube-proxy实现
-   多节点内多Pod通信：跨主机网络解决方案（overlay模型），利用网络插件flannel，calico等实现



## Pod 管理机制

Kubernetes 集群通过pod实现了大量业务应用容器的统一管理

而Kubernetes 也提供了大量的资源对象来对pod进行管理：

*   通过控制器比如deployment来确保 pod的运行和数量符合用户的期望状态
*   通过网络资源比如service来确保pod的应用服务可以被外部的服务来进行访问

Pod 相关的资源对象

*   工作负载型资源: Pod、Deployment、DaemonSet、Replica、StatefulSet、Job、Cronjob、 Operator 
*   服务发现和负载均衡资源: Service、Ingress 
*   配置和存储: configMap、Secret、PersistentVolume、PersistentVolumeChain、DownwardAPI 
*   资源隔离权限控制资源: namespace、nodes、clusterroles、Roles 
*   动态调整资源: HPA、VPA

![image-20250324185012230](pic/image-20250324185012230.png)

## Pod 工作流程

![image-20250324185408008](pic/image-20250324185408008-17428136502251.png)

## **Pod 创建流程**

![image-20250324185445197](pic/image-20250324185445197-17428136868033.png)

1.   **kubectl 发起请求 --> API Server**
     *   kubectl 将请求打包为一个 **HTTP REST 请求**，并发送到 **Kubernetes API Server**。
     *   通过 `kubectl` 命令，API Server 接收到**POST请求**，其中包含了 **Pod的定义信息**（YAML/JSON 格式的PodManifest）。
2.   **API Server 处理请求 --> etcd**
     *   验证请求
         *   进行身份验证（Authentication）和权限验证（Authorization）。
     *   请求合法性校验
         *   通过 **Admission Controllers** 进行一系列的规则检查（比如资源配额、Pod调度限制等）。
     *   对象序列化和持久化
         *   检查请求的YAML/JSON定义是否符合 **Pod Schema**。
3.   **etcd 存储 Pod 定义**
     *   数据存储
     *   新的 Pod 定义被提交至 API Server 并写入 etcd 后，API Server 会通过 Watch 机制将事件推送给监听该资源的控制器，如 Scheduler 和 Controller-Manager。
4.   **Scheduler 调度 Pod --> API Server**
     *   Watch 机制
         *   Scheduler 通过 Watch API Server 监听所有 Pod 对象的变化
         *   当发现一个 `.spec.nodeName == null` 的 Pod（即尚未调度的 Pod），则触发调度流程并进行节点绑定操作
     *   **调度决策**
         *   Scheduler 会从所有**可用的Node中选择一个最优的Node**来运行这个Pod。
         *   Scheduler会考虑以下因素：
             *   **资源约束**：Node的CPU、内存是否足够。
             *   **亲和性/反亲和性**：Pod的亲和性和反亲和性规则。
             *   **污点和容忍度**：节点上是否有污点。
             *   **节点健康状态**：节点是否Ready。
     *   **写回调度结果**
         *   Scheduler 通知API Server 将调度的结果（`spec.nodeName: node01`）更新信息到所有 etcd
5.   **API Server 将度的结果写入 etcd**
6.   **Kubelet创建Pod --> API Server**
     *   Watch 机制
         *   Kubelet 通过 Watch API Server 监听所有 Pod 对象的变化
         *   发现自己需要在本节点上**拉取一个新的Pod**。
     *   **创建Pod沙箱（Pause容器）**
     *   **创建Pod中的业务容器**
     *   **容器状态同步回 API Server**
7.   最终由 API Server更 新信息到 etcd

创建流程自述

-   当使用 `kubectl apply -f pod.yaml` 时，kubectl 会将 YAML 文件中的**Kubernetes 资源对象**（Pod）转换为**JSON 格式的请求体**，并通过 **HTTP POST** 发送到 API Server
    -   **kubectl 作为客户端**，会将 YAML 文件转换为**RESTful API 请求**，API Server 充当**服务端**。
    -   使用的是 **HTTP/2**，并且需要身份认证和权限控制（RBAC）。
    -   API Server 会**先将 Pod 资源保存在内存中（Watch Cache）**，并异步写入 etcd。
-   API Server通过gRPC与etcd通信，将Pod的数据持久化到etcd，**此时Pod的状态是Pending**，因为此时Pod还未被调度到某个节点
-   Scheduler 通过 **watch 机制监听 API Server 中的 Pending Pods**。并通过预选过滤，优选打分，选择出最适合的节点，并将Pod通过POST请求binding到这个目标节点上
-   API Server 将 Pod 的状态从 `Pending` 变为 `Scheduled`。并使用**PUT 请求** 更新 Pod 的状态，并同步到 etcd。同时**API Server 通过 Watch 机制将 Pod 变更事件推送给 Kubelet**。
-   Kubelet 收到 API Server 发送的 Pod 数据后，Kubelet 使用**CRI（Container Runtime Interface）调用 containerd**。containerd 调用**runc**，创建 Pod 的 Linux 容器。Pod 进入**Running**状态。

## Pod 生命周期

### **启动 Pod 流程**

和一个个独立的应用容器一样，Pod 也被认为是相对临时性（而不是长期存在）的实体。

![image-20250324201313430](pic/image-20250324201313430.png)

-   创建指令送到apiserver
-   通知Schedule调度此请求到合适的节点
-   **init容器**
    -   初始化容器（一次性容器，初始化结束，该容器就退出了），独立于主容器之外，即和主容器是隔离的
    -   Pod可以拥有任意数量的init容器，init顺序执行，最后一个执行完成后，才启动主容器
    -   init容器不支持探针检测功能
        -   它主要是为了主容器准备运行环境的功能，比如：给主容器准备配置文件，向主容器的存储写入数据，然后将存储卷挂载到主容器上，下载相关资源，监测主容器依赖服务等
-   **启动后钩子PostStart（Post Start Hook）**: 与主容器同时启动
-   状态监测
    -   **Startup probe：启动探针**：启动探针用来探测这个服务是否起来的，如果探针检查失败，会认为该容器不健康，因此会重新启动容器，如果健康，就会进入下一步
        -   启动探针只检测容器是否启动，容器启动后，后续不再检查
    -   **Liveiness probe（存活探针）**：判断当前Pod是否处于存活状态，是Readiness存活的前提，对应READY状态的m/n的n值
    -   **Readiness Probe（就绪探针**）：判断当前Pod的主应用容器是否可以正常对外提供服务，只有Liveiness为存活，Readiness
        -   Liveness probe和Readiness Probe持续容器终身，只要容器在启动，会不断地探测，如果容器出故障，可以进行一些操作
    -   三个探针就是用来检测容器健康性的
-   Service关联Pod
-   接收用户请求

### **关闭 Pod 流程**

![image-20250324201851235](pic/image-20250324201851235.png)

Kubernetes 中的 **Pod 关闭流程**（Pod Termination）是一个**多阶段的有序过程**，其目的是在**优雅关闭（Graceful Termination）**和**强制删除（Force Deletion）**之间取得平衡。这个流程涉及**负载均衡器（Service 代理）、preStop 钩子、API Server、Kubelet、etcd、containerd 和 runc** 等多个组件的协作。

整个流程可分为**5 个主要阶段**

**Pod 关闭流程的状态变化**

| **阶段**   | **状态**      | **描述**                                    |
| ---------- | ------------- | ------------------------------------------- |
| **阶段 1** | `Running`     | Pod 处于正常运行状态                        |
| **阶段 2** | `Terminating` | `kubectl delete` 触发了删除事件             |
| **阶段 3** | `Terminating` | 体面终止限期内，preStop 钩子和 SIGTERM 执行 |
| **阶段 4** | `Terminating` | Pod 从 Service 的 Endpoints 中被删除        |
| **阶段 5** | **已删除**    | 体面终止限期结束，Pod 彻底被清除            |

**强制删除（Force Deletion）流程**

**当指定 `--grace-period=0` 时，流程的关键变化如下：**

| **组件**              | **行为变化**         | **解释**                                   |
| --------------------- | -------------------- | ------------------------------------------ |
| **体面终止**          | **跳过**             | 不执行宽限期，直接发出**SIGKILL**          |
| **preStop 钩子**      | **跳过**             | 不会执行 preStop 脚本                      |
| **Service Endpoints** | **立即删除**         | Pod 会立刻被从 Endpoints 中删除            |
| **Pod 终止状态**      | 立即终止             | API Server 将 Pod 立即标记为 `Terminating` |
| **Kubelet 删除**      | **立即发出 SIGKILL** | Kubelet 直接调用 SIGKILL                   |
| **Pod 删除**          | **立即删除**         | Kubelet 直接调用 API Server 删除           |

#### 阶段 1：请求删除 Pod

1.   **发起删除请求**：

     -   通过 `kubectl delete pod <pod-name>`，kubectl 向 API Server 发起一个**DELETE 请求**。

     -   这时，API Server 会**立即**将 Pod 的**状态标记为 Terminating**。

     -   **优雅终止期（graceful termination period）设置**

         -   当执行 `kubectl delete` 时，可以通过 `--grace-period=<seconds>` 指定**体面终止限期**。

         -   如果未指定，默认为 30 秒。

2.   **通知 Controller 和 Service**

     *   API Server 通过**watch 机制**通知 **Controller Manager** 和 **Service 代理（例如 kube-proxy）**。
     *   **Service 代理（例如 kube-proxy）**会将 Pod 从 **Endpoints** 中删除，从而不再将流量路由到该 Pod

#### 阶段 2：通知 Kubelet

1.   **Watch 机制通知 Kubelet**：
     -   API Server 向 Node 上的 Kubelet 发送一个**Pod 变更事件**，标识该 Pod 处于 **Terminating** 状态。
2.   **Kubelet 处理 Pod 变更**：
     *   Kubelet 在收到变更事件后，**检查 Pod 的体面终止限期（graceful termination period）**。
     *   Kubelet 确保 Pod 在**宽限期内停止运行**。

#### 阶段 3：执行 preStop 钩子和终止容器

![image-20250324202547812](pic/image-20250324202547812.png)

ubelet 会 **几乎同时**：

-   执行容器的 `preStop` 钩子（在容器内部执行）
-   向主容器进程发送 `SIGTERM`

-   两者都在 `terminationGracePeriodSeconds` 这个宽限期内完成
-   如果容器在这段时间内没退出，则会被强制 SIGKILL

#### 阶段 4：移除 Pod Endpoints（从负载均衡中删除）

**更新 Service Endpoints**：

-   prestop钩子和Kubelet向Pod发送SIGTERM以及通过**Endpoints Controller**和**kube-proxy**将 Pod 从 Service 的 Endpoints 中移除。这三个操作同步执行
-   在体面终止限期的**开始时**，API Server 就会通过**Endpoints Controller**和**kube-proxy**将 Pod 从 Service 的 Endpoints 中移除。
-   **原因**：即使 Pod 仍在运行，但为了防止发送到即将被终止的 Pod 的流量，提前将其从流量路径中删除。



#### 从 etcd 中删除 Pod

**Kubelet 向 API Server 发送删除请求**：

-   如果 Kubelet 发现 Pod 进程已完全终止（所有容器都已关闭），Kubelet 向 API Server 发送 **DELETE 请求**。

**API Server 通知 etcd 删除 Pod**：

-   API Server 通过 gRPC 调用 etcd 删除与 Pod 相关的

**从 etcd 中移除 Pod 对象**：

-   Pod 对象从 etcd 中被物理删除，所有与之相关的**watch 监听器（Kubelet, Controller, Scheduler）**都会立即收到事件。



### 设置终止宽限期

```yaml
spec:
 terminationGracePeriodSeconds: 3600  # Pod 级别设置，等价于--grace-period=3600
 containers:
  - name: test
    image: ...
```



### 两种钩子PostStart和PreStop

根据上面Pod的启动流程，当容器中的进程启动前或者容器中的进程终止之前都会有一些额外的动作执 行，这是由kubelet所设置的，在这里，我们称之为 **pod hook。**

对于Pod的流程启动，主要有两种钩子：

-   **postStart**：**容器创建完成后立即运行**，不保证一定会于容器中ENTRYPOINT之前运行,而Init Container可以实现
-   **preStop**：**容器终止操作之前立即运行**，在其完成前会阻塞删除容器的操作调用

#### Post Start Hook

```yaml
vim pod-poststart.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-poststart
spec:
  containers:
    - name: busybox
      image: busybox:1.32.0
      lifecycle:
        postStart:
          exec:
            command: ["/bin/sh","-c","echo lifecycle poststart at $(date) > /tmp/poststart.log"]
      command: ['sh', '-c', 'echo The app is running at $(date) ! && sleep 3600']
```

#### Pre Stop Hook

实现pod对象移除之前，需要做一些清理工作，比如:释放资源，解锁等

```yaml
vim pod-prestop.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-prestop
spec:
  volumes:
  - name: vol-prestop
    hostPath:
      path: /tmp
  containers:
  - name: prestop-pod-container
    image: busybox:1.32.0
    volumeMounts:
    - name: vol-prestop
      mountPath: /tmp
    command: ['sh', '-c', 'echo The app is running at $(date) ! && sleep 3600']
    lifecycle:
      postStart:
        exec:
          command: ['/bin/sh', '-c', 'echo lifecycle poststart at $(date) > /tmp/poststart.log']
      preStop:
        exec:
          command: ['/bin/sh', '-c', 'echo lifecycle prestop at $(date) > /tmp/prestop.log']
```

## Pod 状态

### Pod phase阶段（相位）

![image-20250324205018328](pic/image-20250324205018328.png)

| 取值                | 描述                                                         |
| :------------------ | :----------------------------------------------------------- |
| `Pending`（悬决）   | Pod 已被 Kubernetes 系统接受，但有一个或者多个容器尚未创建亦未运行。此阶段包括等待 Pod 被调度的时间和通过网络下载镜像的时间。 |
| `Running`（运行中） | Pod 已经绑定到了某个节点，Pod 中所有的容器都已被创建。至少有一个容器仍在运行，或者正处于启动或重启状态。 |
| `Succeeded`（成功） | Pod 中的所有容器都已成功结束，并且不会再重启。               |
| `Failed`（失败）    | Pod 中的所有容器都已终止，并且至少有一个容器是因为失败终止。也就是说，容器以非 0 状态退出或者被系统终止，且未被设置为自动重启。 |
| `Unknown`（未知）   | 因为某些原因无法取得 Pod 的状态。这种情况通常是因为与 Pod 所在主机通信失败。 |

### Pod 的启动流程状态

| 流程状态        | 描述                              |
| --------------- | --------------------------------- |
| PodScheduled    | Pod被调度到某一个节点             |
| Ready           | 准备就绪，Pod可以处理请求         |
| Initialized     | Pod中所有初始init容器启动完毕     |
| Unschedulable   | 由于资源等限制，导致pod无法被调度 |
| ContainersReady | Pod中所有的容器都启动完毕了       |

### **Pod重启策略（面试题）**

**注意：同一个 Pod 内所有容器只能使用统一的重启策略**

| 重启策略  | 描述                                                         |
| --------- | ------------------------------------------------------------ |
| Always    | 无论退出码exit code是否为0，都要重启，即只要退出就重启，并且重启次数并没有限制，此为默认值 |
| OnFailure | 此为**默认值**, 容器终止运行退出码exit code不为0时才重启,重启次数并没有限制 |
| Never     | 无论何种退出码exit code,Pod都不重启。主要针对Job和CronJob    |

```yaml
spec:
  containers:
  - image: busybox:1.32.0
    name: myapp
  restartPolicy: OnFailure #默认Always策略，会不断重启
```

### **Pod 镜像拉取状态（面试题）**

| 拉取策略     | 描述                                                         |
| ------------ | ------------------------------------------------------------ |
| Always       | 总是拉取新镜像，注意：如果**镜像的Tag为latest**，拉取策略为always或 ifNotPresent 都会重新拉取镜像 |
| IfNotPresent | 此为**默认值**，如果本地不存在的话，再拉取新镜像，例外情况:如果镜像的Tag为 latest，仍会重新拉取镜像 |
| Never        | 只使用本地的镜像，从不获取新镜像                             |

```yaml
spec:
  containers:
  - image: busybox:1.32.0
    imagePullPolicy: IfNotPresent
    name: myapp
  restartPolicy: OnFailure #默认Always策略，会不断重启
```



# Pod 的健康状态监测

