#!/usr/bin/env python3
"""
Start API Server
---------------
Convenience script to start the FastAPI server.

Usage:
    python scripts/start_api.py
    
    Or directly:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import os

# Check if uvicorn is installed
try:
    import uvicorn
except ImportError:
    print("❌ Error: uvicorn not installed")
    print("Install with: pip install uvicorn[standard]")
    sys.exit(1)

# Check if vector store exists
vectorstore_path = "data/vectorstore/faiss.index"
if not os.path.exists(vectorstore_path):
    print("\n" + "=" * 70)
    print("⚠️  WARNING: Vector store not found!")
    print("=" * 70)
    print(f"\nMissing: {vectorstore_path}")
    print("\nThe API will start but the /chat endpoint won't work.")
    print("\n📝 To fix, run:")
    print("   1. python scripts/scrape_website.py")
    print("   2. python scripts/process_data.py")
    print("   3. python scripts/build_vectorstore.py")
    print("\nContinuing to start API anyway...")
    print("=" * 70 + "\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Exiting...")
        sys.exit(0)

print("\n" + "=" * 70)
print("🚀 STARTING SRM CHATBOT API")
print("=" * 70)
print("\n📝 Configuration:")
print("   Host: 0.0.0.0 (accessible from network)")
print("   Port: 8000")
print("   Reload: Enabled (auto-reload on code changes)")
print("\n🌐 Access:")
print("   API Docs:  http://localhost:8000/docs")
print("   Health:    http://localhost:8000/health")
print("   Chat:      POST http://localhost:8000/chat")
print("\n💡 Tips:")
print("   - Visit /docs for interactive API testing")
print("   - Press Ctrl+C to stop the server")
print("   - Server auto-reloads on file changes")
print("=" * 70 + "\n")

# Start the server
try:
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
except KeyboardInterrupt:
    print("\n\n👋 Server stopped!")
except Exception as e:
    print(f"\n❌ Error starting server: {str(e)}")
    sys.exit(1)