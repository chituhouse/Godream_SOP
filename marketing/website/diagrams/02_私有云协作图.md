# 图谱：私有云协作（相对路径 + NAS 映射）

```mermaid
flowchart LR
  A[用户 A 电脑\nGoDream] -->|映射同一共享目录| NAS[(NAS/私有云共享目录)]
  B[用户 B 电脑\nGoDream] -->|映射同一共享目录| NAS
  NAS --> P[项目文件夹\n(相对路径 + SQLite)]
  P --> A
  P --> B
```

