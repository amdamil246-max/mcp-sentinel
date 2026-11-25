import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import init_db, SessionLocal
from app.models.user import User, UserRole
from app.models.server import MCPServer
from app.models.tool import RegisteredTool
from app.models.policy import Policy
from app.core.security import get_password_hash

# Routers
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.mcp_servers import router as servers_router
from app.api.tools import router as tools_router
from app.api.gateway_invoke import router as gateway_router
from app.api.approvals import router as approvals_router
from app.api.security import router as security_router
from app.api.policies import router as policies_router
from app.api.audit import router as audit_router
from app.api.ai_analyst import router as ai_analyst_router
from app.api.websocket import router as ws_router
from app.api.demo import router as demo_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("mcp-sentinel")

def seed_initial_data():
    """Seeds default administrator, analyst, baseline MCP servers, tools, and policies."""
    with SessionLocal() as db:
        # 1. Seed Users
        if not db.query(User).filter(User.username == "admin").first():
            admin_user = User(
                username="admin",
                email="admin@mcpsentinel.local",
                hashed_password=get_password_hash("SentinelAdmin2026!"),
                full_name="Principal Security Administrator",
                role=UserRole.ADMINISTRATOR,
                is_active=True
            )
            analyst_user = User(
                username="analyst",
                email="analyst@mcpsentinel.local",
                hashed_password=get_password_hash("AnalystPass2026!"),
                full_name="SOC Security Analyst",
                role=UserRole.SECURITY_ANALYST,
                is_active=True
            )
            viewer_user = User(
                username="viewer",
                email="viewer@mcpsentinel.local",
                hashed_password=get_password_hash("ViewerPass2026!"),
                full_name="Compliance Auditor",
                role=UserRole.VIEWER,
                is_active=True
            )
            db.add_all([admin_user, analyst_user, viewer_user])
            logger.info("Default security users initialized.")

        # 2. Seed Baseline MCP Servers
        if not db.query(MCPServer).filter(MCPServer.id == "terminal-server").first():
            term_server = MCPServer(
                id="terminal-server",
                name="System Terminal MCP Server",
                description="Provides terminal command execution and system diagnostic inspection tools.",
                connection_type="stdio",
                command="python",
                args=["mcp_servers/mock_terminal_server/server.py"],
                is_enabled=True,
                health_status="healthy",
                last_connected_at=datetime.utcnow()
            )
            fs_server = MCPServer(
                id="filesystem-server",
                name="Secure Filesystem MCP Server",
                description="Provides read, write, and directory indexing capabilities across workspace sandboxes.",
                connection_type="stdio",
                command="python",
                args=["mcp_servers/mock_filesystem_server/server.py"],
                is_enabled=True,
                health_status="healthy",
                last_connected_at=datetime.utcnow()
            )
            db.add_all([term_server, fs_server])

            # 3. Seed Registered Tools
            tools = [
                RegisteredTool(
                    id="terminal-server:run_command",
                    server_id="terminal-server",
                    name="run_command",
                    description="Executes a shell command inside the system environment.",
                    input_schema={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
                    permission_level="execute",
                    trust_level="monitored",
                    is_enabled=True,
                    requires_approval=False
                ),
                RegisteredTool(
                    id="terminal-server:get_system_status",
                    server_id="terminal-server",
                    name="get_system_status",
                    description="Retrieves real-time system performance, CPU, memory, and firewall metrics.",
                    input_schema={"type": "object", "properties": {}},
                    permission_level="read",
                    trust_level="trusted",
                    is_enabled=True,
                    requires_approval=False
                ),
                RegisteredTool(
                    id="terminal-server:search_logs",
                    server_id="terminal-server",
                    name="search_logs",
                    description="Queries historical system log messages with a keyword filter.",
                    input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
                    permission_level="read",
                    trust_level="trusted",
                    is_enabled=True,
                    requires_approval=False
                ),
                RegisteredTool(
                    id="filesystem-server:read_file",
                    server_id="filesystem-server",
                    name="read_file",
                    description="Reads raw contents of a target file from disk.",
                    input_schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
                    permission_level="read",
                    trust_level="trusted",
                    is_enabled=True,
                    requires_approval=False
                ),
                RegisteredTool(
                    id="filesystem-server:write_file",
                    server_id="filesystem-server",
                    name="write_file",
                    description="Writes text or code content to a designated file path.",
                    input_schema={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
                    permission_level="write",
                    trust_level="monitored",
                    is_enabled=True,
                    requires_approval=True
                ),
                RegisteredTool(
                    id="filesystem-server:list_directory",
                    server_id="filesystem-server",
                    name="list_directory",
                    description="Lists files and subdirectories within a given folder path.",
                    input_schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
                    permission_level="read",
                    trust_level="trusted",
                    is_enabled=True,
                    requires_approval=False
                )
            ]
            db.add_all(tools)

        # 4. Seed Baseline Security Policies
        if not db.query(Policy).filter(Policy.id == "POL-CMD-001").first():
            p1 = Policy(
                id="POL-CMD-001",
                name="Strict Destructive Command Prevention",
                description="Blocks rm -rf, disk wiping, raw format, and unauthorized privilege escalation.",
                category="command",
                rule_type="deny",
                configuration={"auto_block": True, "alert_severity": "Critical"},
                is_active=True,
                priority=10
            )
            p2 = Policy(
                id="POL-FILE-002",
                name="Workspace Sandbox & Sensitive File Isolation",
                description="Prevents directory traversal and blocks access to .env, SSH keys, SAM, and cloud credentials.",
                category="filesystem",
                rule_type="deny",
                configuration={"enforce_canonical_path": True, "block_forbidden_files": True},
                is_active=True,
                priority=20
            )
            p3 = Policy(
                id="POL-PI-003",
                name="Prompt Injection & Jailbreak Neutralization",
                description="Detects instruction overrides and blocks adversarial tool responses from reaching agents.",
                category="prompt_injection",
                rule_type="deny",
                configuration={"block_injection_responses": True},
                is_active=True,
                priority=30
            )
            p4 = Policy(
                id="POL-APPR-004",
                name="High Impact Write & Administrative Operations Approval",
                description="Enforces human authorization workflow for operations exceeding risk threshold.",
                category="general",
                rule_type="require_approval",
                configuration={"risk_threshold": 50.0, "expiration_seconds": 300},
                is_active=True,
                priority=40
            )
            db.add_all([p1, p2, p3, p4])

        db.commit()
        logger.info("MCP Sentinel baseline servers, tools, and policies seeded successfully.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_initial_data()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Security Firewall & Execution Protection Gateway for AI Agents and MCP Servers",
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(servers_router, prefix=settings.API_V1_PREFIX)
app.include_router(tools_router, prefix=settings.API_V1_PREFIX)
app.include_router(gateway_router, prefix=settings.API_V1_PREFIX)
app.include_router(approvals_router, prefix=settings.API_V1_PREFIX)
app.include_router(security_router, prefix=settings.API_V1_PREFIX)
app.include_router(policies_router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_analyst_router, prefix=settings.API_V1_PREFIX)
app.include_router(demo_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_router)

@app.get("/")
async def root():
    return {
        "product": settings.PROJECT_NAME,
        "tagline": settings.PROJECT_TAGLINE,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
