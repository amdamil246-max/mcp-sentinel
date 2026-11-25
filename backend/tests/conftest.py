import os

os.environ["DATABASE_URL"] = "sqlite:///./test_sentinel.db"
os.environ["ENVIRONMENT"] = "testing"
