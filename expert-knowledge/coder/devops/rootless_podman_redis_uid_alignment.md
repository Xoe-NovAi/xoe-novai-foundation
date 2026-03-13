# 패턴: Rootless Podman에서의 Redis 권한 정렬 (Redis UID Alignment)

## 문제 (Problem)
Rootless Podman 환경에서 Redis 컨테이너(기본 UID 999)가 호스트 디렉토리를 볼륨으로 매운 경우, RDB 스냅샷 저장 시 `Permission denied` 오류가 발생하며 데이터 수정 명령이 중단됨 (`MISCONF` 오류).

## 해결책 (Solution)
`docker-compose.yml`에서 Redis 서비스의 `user`를 호스트의 UID와 일치하도록 명시적으로 설정함.

```yaml
services:
  redis:
    image: redis:7.4.1
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    # ... rest of config
```

## 효과 (Benefits)
- Redis가 `/data` 디렉토리에 RDB 파일을 정상적으로 쓸 수 있음.
- `stop-writes-on-bgsave-error`로 인한 서비스 중단 방지.
- 호스트 시스템과의 일관된 권한 관리.
