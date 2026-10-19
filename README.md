<div align="center">

# 🔕 Failure-Hunter
### **Static AST Analyzer for Detecting Swallowed Errors & Silent Failures**
*Hunting Empty Catches, Silent Fallbacks, and Masked Exceptions Before They Kill Production.*

[![License: MIT](https://img.shields.io/badge/License-MIT-0B1220?style=for-the-badge&logoColor=white)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-0B1220?style=for-the-badge&logo=python&logoColor=38BDF8)](https://python.org)
[![Dependencies: Zero](https://img.shields.io/badge/Dependencies-Zero-0B1220?style=for-the-badge&logoColor=10B981)](pyproject.toml)
[![Architecture: PSTACK](https://img.shields.io/badge/PSTACK-Mandate_2_Compliant-0B1220?style=for-the-badge&logoColor=F59E0B)](https://github.com/sinergiefek)

---

> *"The most lethal bugs in distributed systems never crash the server. They catch the exception, execute `pass`, return a fake `None`, and corrupt data in total silence."*

</div>

---

### 💡 The Silent Failure Epidemic

Over 80% of catastrophic production outages and data-corruption incidents are preceded by **swallowed exceptions**:
* ❌ **The `except: pass` Trap:** A database connection drops, but the exception block silently passes. The caller assumes the record was persisted.
* ❌ **The Fake Fallback Trap:** A function catches a critical authorization or payment error and quietly executes `return None` without logging.
* ❌ **The Bare `except:` Trap:** Catches `BaseException`, silently neutralizing `KeyboardInterrupt` and `SystemExit`, turning simple background workers into unkillable zombie processes.

**Failure-Hunter** parses the codebase's **Abstract Syntax Tree (AST)** directly in milliseconds to find and terminate these patterns before code reaches `main`.

---

### 🛡️ Rules Enforced

| Rule ID | Severity | Description |
| :--- | :---: | :--- |
| **`SILENT_001`** | 🚨 **FATAL** | Empty `except` block containing only `pass` or `...` (Exception swallowed without telemetry). |
| **`SILENT_002`** | ⚠️ **HIGH** | Bare `except:` statement (masks critical signals like `KeyboardInterrupt` and `SystemExit`). |
| **`SILENT_003`** | 🚨 **FATAL** | Silent `return` or `return None` inside `except` handler without any logger or print statement. |
| **`SILENT_004`** | ⚠️ **MEDIUM** | Exception variable captured (`except Exception as e:`) but `e` is never referenced or logged. |

---

### 🚀 Quickstart

#### 1. Run via CLI

```bash
# Scan current directory recursively
failure-hunter .

# Scan specific module or file
failure-hunter src/backend/database.py
```

#### Output Example:
```
🔍 Hunting silent failures in: /var/www/app ...

🚨 [ALERT] Found 2 silent failure violation(s):

  • services/payment.py:42:8 [SILENT_001]
    Message: Empty except block with 'pass' or '...' (Exception swallowed completely)
    Code:    pass

  • controllers/order.py:89:12 [SILENT_003]
    Message: Silent fallback 'return' or 'return None' inside except handler without logging
    Code:    return None
```

#### 2. CI/CD GitHub Actions Integration

Add Failure-Hunter as a required pre-merge gate in `.github/workflows/ci.yml`:

```yaml
name: Zero-Silent-Failures Gate

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Failure-Hunter
        run: pip install failure-hunter
      - name: Scan AST for Silent Errors
        run: failure-hunter src/
```

---

### 🏢 Open Core & Enterprise Capabilities

| Capability | Community (MIT) | Enterprise Code-Health Engine |
| :--- | :---: | :---: |
| Python AST Scanner (SILENT_001 - SILENT_004) | ✅ | ✅ |
| Zero External Dependencies | ✅ | ✅ |
| CLI Tool with Non-Zero Exit Code | ✅ | ✅ |
| **Polyglot AST Support (TypeScript / JavaScript / PHP)** | ❌ | 👑 **Enterprise** |
| **Autonomous AI Remediation (Auto-Fix PR Generator)** | ❌ | 👑 **Enterprise** |
| **Production Flight Recorder / Sentry Cross-Correlator**| ❌ | 👑 **Enterprise** |

For Enterprise code health audits, automated remediation pipelines, or architecture advisory, visit [Sinergi Mitra Visitama](https://sinergimitravisitama.my.id).

---

### 📄 License

Licensed under the permissive [MIT License](LICENSE).  
Copyright (c) 2026 Setijono (Sinergi Mitra Visitama).
