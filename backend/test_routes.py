#!/usr/bin/env python3

import main

def list_routes():
    print("FastAPI Application Routes:")
    print("=" * 50)
    
    for route in main.app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"{methods:<10} {route.path}")
        elif hasattr(route, 'path'):
            print(f"{'INCLUDE':<10} {route.path}")
    
    print("=" * 50)
    print("PostgreSQL endpoints are now available under /api/db/ prefix")
    print("Example endpoints:")
    print("  POST   /api/db/init")
    print("  GET    /api/db/chats")
    print("  POST   /api/db/chats")
    print("  GET    /api/db/projects")
    print("  POST   /api/db/projects")
    print("  GET    /api/db/health")

if __name__ == "__main__":
    list_routes()