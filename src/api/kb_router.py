from __future__ import annotations
import os
import aiofiles
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List

kb_router = APIRouter(tags=["Knowledge Base"])

KB_DIR = Path("knowledge_base")

class KBFile(BaseModel):
    path: str
    content: str

class KBFileInfo(BaseModel):
    path: str
    name: str
    size: int

def validate_path(file_path: str) -> Path:
    """Validate to prevent path traversal and ensure it's a .md file."""
    if ".." in file_path or file_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path format.")
    
    full_path = KB_DIR / file_path
    
    try:
        full_path.resolve().relative_to(KB_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Path traversal detected.")
    
    if full_path.suffix != ".md":
        raise HTTPException(status_code=400, detail="Only .md files are supported.")
        
    return full_path

@kb_router.get("/", response_model=List[KBFileInfo])
async def list_files():
    """Liệt kê toàn bộ danh sách file trong knowledge_base."""
    files = []
    if not KB_DIR.exists():
        return files
        
    for root, _, filenames in os.walk(KB_DIR):
        for name in filenames:
            if name.endswith(".md"):
                full_path = Path(root) / name
                rel_path = full_path.relative_to(KB_DIR).as_posix()
                files.append(KBFileInfo(
                    path=rel_path,
                    name=name,
                    size=full_path.stat().st_size
                ))
    return files

@kb_router.get("/file")
async def get_file(path: str):
    """Đọc nội dung một file .md."""
    file_path = validate_path(path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
        
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        content = await f.read()
        
    return {"path": path, "content": content}

@kb_router.post("/file")
async def save_file(data: KBFile, request: Request):
    """Tạo mới hoặc cập nhật file .md."""
    file_path = validate_path(data.path)
    
    # Tự động tạo thư mục cha nếu chưa có
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(data.content)
        
    # Gọi hàm reload từ container để cập nhật RAG index (chạy ngầm)
    container = getattr(request.app.state, "container", None)
    if container and container.fast_layer and container.fast_layer.knowledge:
        import asyncio
        asyncio.create_task(container.fast_layer.knowledge.reload())
        
    return {"status": "success", "message": f"File '{data.path}' saved and RAG index reloaded."}

@kb_router.delete("/file")
async def delete_file(path: str, request: Request):
    """Xóa file .md."""
    file_path = validate_path(path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
        
    file_path.unlink()
    
    # Dọn thư mục rỗng nếu cần
    parent = file_path.parent
    if parent != KB_DIR and not any(parent.iterdir()):
        try:
            parent.rmdir()
        except OSError:
            pass # Vẫn còn file khác
            
    # Gọi hàm reload từ container để cập nhật RAG index (chạy ngầm)
    container = getattr(request.app.state, "container", None)
    if container and container.fast_layer and container.fast_layer.knowledge:
        import asyncio
        asyncio.create_task(container.fast_layer.knowledge.reload())
        
    return {"status": "success", "message": f"File '{path}' deleted and RAG index reloaded."}
