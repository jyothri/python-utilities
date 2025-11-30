# Migration Plan — Python -> Spring Boot (Gradle)

This document captures the migration plan to convert the existing Python `python-utilities` project into an equivalent Java Spring Boot console application using Gradle as the build tool.

## Goal
- Replace the Python CLI (parses certificate listings, filters certificates expiring within 10 days, prints and emails an HTML table) with a Java Spring Boot console application (CommandLineRunner) built with Gradle.

## Deliverables
- Gradle-based Spring Boot project skeleton
- Java classes and packages: model, services (parser, formatting, email), main runner
- Configuration via `application.yml` and environment variables (e.g. `PLUNK_API_KEY`)
- Unit tests (parsing, email service) and a basic CI workflow
- README and migration notes

## Project structure (proposed)

```
utilities/
├── build.gradle.kts       # Gradle build script (Kotlin DSL)
├── settings.gradle.kts
├── gradle/                # optional gradle wrapper
├── src/main/java/com/jyothri/utilities/
│   ├── Application.java
│   ├── MainRunner.java
│   ├── config/PlunkProperties.java
│   ├── model/Certificate.java
│   └── service/
│       ├── ParserService.java
│       ├── FormattingService.java
│       └── EmailService.java
├── src/main/resources/application.yml
├── src/test/java/...      # unit tests
└── README.md
```

## Gradle configuration (recommendation)

- Use Gradle with the Spring Boot plugin and the Kotlin DSL (`build.gradle.kts`). Example `build.gradle.kts`:

```kotlin
plugins {
  id("org.springframework.boot") version "3.1.0"
  id("io.spring.dependency-management") version "1.1.0"
  java
}

group = "com.jyothri"
version = "0.1.0"
java.sourceCompatibility = JavaVersion.VERSION_17

repositories {
  mavenCentral()
}

dependencies {
  implementation("org.springframework.boot:spring-boot-starter")
  implementation("org.springframework.boot:spring-boot-starter-webflux") // for WebClient
  testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
  useJUnitPlatform()
}
```

Commands:

```bash
./gradlew build
./gradlew bootJar
java -jar build/libs/<project-name>-0.1.0.jar /path/to/input.txt
```

## Mapping: Python -> Java
- `src/main.py` -> `MainRunner.java` (implements CommandLineRunner, uses ApplicationArguments)
- `utils/helpers.py`:
  - `Certificate` -> `model/Certificate.java` (use `OffsetDateTime expiryDate`)
  - `parse_certificates()` -> `service/ParserService.java`
  - `format_certificates_as_html_table()` -> `service/FormattingService.java`
- `utils/email_sender.py` -> `service/EmailService.java` (use WebClient)
- `input.txt` -> passed at runtime as CLI argument (or placed in resources for testing)

## Key technical decisions

- Use `java.time.OffsetDateTime` for timezone-aware expiry parsing and comparisons. DateTimeFormatter pattern: `yyyy-MM-dd HH:mm:ssXXX`.
- Use Spring's `WebClient` (from `spring-boot-starter-webflux`) to call the Plunk API. Keep the payload format configurable (some Plunk accounts expect `html` vs `body`).
- Configuration via `application.yml` and environment variables (e.g., `PLUNK_API_KEY`). Use `@ConfigurationProperties` to bind properties.
- CLI argument parsing via `ApplicationArguments` (Spring Boot). First positional arg is the input file path.

## Implementation tasks (detailed)

1. Project skeleton (Gradle) — create `build.gradle`, `settings.gradle`, gradle wrapper, base package and `Application.java`.
2. Model — `Certificate.java` with fields and `OffsetDateTime expiryDate`.
3. ParserService — read file line-by-line and build `Certificate` objects; robust to missing fields.
4. FormattingService — produce an HTML table string for email bodies.
5. EmailService — configurable API url and key, send JSON payload to Plunk using `WebClient`, handle non-2xx responses.
6. MainRunner — accept `file_path` CLI argument, call services, filter using `OffsetDateTime.now(ZoneOffset.UTC).plusDays(10)`, print and send email if needed.
7. Tests — unit tests for parser and an HTTP-mocked email service. Use JUnit 5 and Mockito or MockWebServer for HTTP.
8. CI — add GitHub Actions workflow to run `./gradlew test` on push and PRs.

## Config sample (`application.yml`)

```yaml
plunk:
  api:
    key: ${PLUNK_API_KEY:}
    url: https://api.useplunk.com/v1/send
  recipient: ${PLUNK_RECIPIENT:user@example.com}
```

## Tests & verification
- ParserService: test with `input.txt` fixtures (happy and malformed cases).
- EmailService: use `MockWebServer` to assert outgoing requests and headers (Authorization: Bearer).
- Integration: run the fat jar against `input.txt` and verify printed output and that the EmailService attempted to POST (in local dev, point to a mock server).

## Timeline/Estimates (single developer)
- Skeleton & wiring: 1–2 hours
- Model + parser + tests: 2–4 hours
- Email service + tests: 1–2 hours
- CLI wiring, config polish, README: 1 hour
- CI/cleanup: 0.5–1 hour
- Total: ~6–10 hours

## Risks & mitigations
- Date parsing differences — provide flexible parsing and fallback formats.
- API contract mismatch — make payload keys configurable and test against a staging endpoint.
- Secrets leakage — read API key from env (`PLUNK_API_KEY`) and avoid committing any secret to VCS.

## Next actions I can take now
- Generate the Gradle project skeleton and create initial Java files (Application, MainRunner, model and services stubs).
- Implement ParserService using the sample `input.txt` and provide unit tests.

Pick one and I will start implementing it in your workspace.
