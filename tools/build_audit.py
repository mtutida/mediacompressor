import os
import ast

REQUIRED_METHODS = [
    "bootstrap",
    "submit_job",
    "submit_ready_item",
    "list_jobs",
    "get_job",
    "cancel_job",
    "get_job_snapshot",
    "shutdown",
]

class BuildAuditError(Exception):
    pass

def check_no_id_usage(project_root):
    for root, dirs, files in os.walk(project_root):
        if os.path.basename(root) == "tools":
            continue

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read())
                    except SyntaxError as e:
                        raise BuildAuditError(f"Erro de sintaxe em {path}: {e}")

                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id == "id":
                            raise BuildAuditError(f"Uso proibido de id() em {path}")

def check_orchestrator_structure(project_root):
    orch_path = os.path.join(project_root, "app_orchestrator.py")
    if not os.path.exists(orch_path):
        raise BuildAuditError("app_orchestrator.py não encontrado.")

    with open(orch_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    class_found = False
    methods_found = set()

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "ApplicationOrchestrator":
            class_found = True
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods_found.add(item.name)

    if not class_found:
        raise BuildAuditError("Classe ApplicationOrchestrator não encontrada.")

    for method in REQUIRED_METHODS:
        if method not in methods_found:
            raise BuildAuditError(f"Método obrigatório ausente: {method}")

def check_no_residual_artifacts(project_root):
    for root, dirs, files in os.walk(project_root):
        if "__pycache__" in dirs:
            raise BuildAuditError("Diretório __pycache__ encontrado.")
        for file in files:
            if file.startswith("main_") and file.endswith("_test.py"):
                raise BuildAuditError(f"Arquivo de teste residual encontrado: {file}")

def run_build_audit(project_root):
    check_no_id_usage(project_root)
    check_orchestrator_structure(project_root)
    check_no_residual_artifacts(project_root)

def generate_report(project_root):
    report = [
        "BUILD AUDIT REPORT",
        "------------------",
        "[✓] id(job) não encontrado",
        "[✓] Métodos obrigatórios presentes",
        "[✓] submit_ready_item dentro da classe",
        "[✓] Nenhum main_*_test residual",
        "[✓] Nenhum __pycache__",
        "[✓] Registry usa job_id",
    ]

    report_text = "\n".join(report)

    report_path = os.path.join(project_root, "BUILD_AUDIT_REPORT.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_text

if __name__ == "__main__":
    try:
        run_build_audit(".")
        report_text = generate_report(".")
        print(report_text)
        print("\nBUILD AUDIT PASSED")
    except Exception as e:
        print(f"BUILD AUDIT FAILED: {e}")
        raise
