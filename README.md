# Fullstack Demo: Spring Boot 3 + Vue 3 (Vite)

이 프로젝트는 간단한 풀스택 예제입니다.

- **Backend**: Spring Boot 3, Gradle, Java 17  
- **Frontend**: Vue 3, Vite  
- **API**: `GET /api/hello`

## 프로젝트 구조

```text
cicd-test/
  backend/   # Spring Boot 3 + Gradle 백엔드
  frontend/  # Vue 3 + Vite 프론트엔드
```

---

## 1. 백엔드 실행 (Spring Boot)

### 1-1. 요구 사항

- Java 17 이상 (JDK 17)
- Gradle는 래퍼가 없으므로, **로컬에 Gradle가 설치**되어 있어야 합니다.

### 1-2. 실행 방법

```bash
cd backend
gradle bootRun
```

기본 포트는 `http://localhost:8080` 입니다.

확인용 엔드포인트:

- `GET http://localhost:8080/api/hello`

---

## 2. 프론트엔드 실행 (Vue 3 + Vite)

### 2-1. 요구 사항

- Node.js (18 이상 권장)

### 2-2. 의존성 설치

```bash
cd frontend
npm install
```

### 2-3. 개발 서버 실행

```bash
npm run dev
```

Vite 기본 포트는 `http://localhost:5173` 입니다.

---

## 3. 프론트엔드와 백엔드 연동

- 프론트엔드는 `/api/hello` 경로로 요청을 보냅니다.
- `frontend/vite.config.js` 에서 **프록시 설정**이 되어 있어,
  Vite 개발 서버(포트 5173)가 **백엔드(포트 8080)** 로 `/api` 요청을 프록시합니다.

```js
// frontend/vite.config.js 중 일부
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
    },
  },
},
```

따라서, 다음 순서로 실행하면 됩니다.

1. 터미널 A: `cd backend && gradle bootRun`
2. 터미널 B: `cd frontend && npm run dev`
3. 브라우저에서 `http://localhost:5173` 접속

화면에서 `/api/hello` 호출 결과가 표시됩니다.

