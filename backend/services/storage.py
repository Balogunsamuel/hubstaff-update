import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO
from fastapi import UploadFile, HTTPException, status
from config import settings
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class StorageError(Exception):
    """Custom exception for storage operations"""
    pass

class StorageService:
    """File storage service with support for local and cloud storage"""
    
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.upload_dir = settings.uploads_path
        
        # Initialize Supabase client if using Supabase storage
        if self.storage_type == "supabase":
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise StorageError("Supabase URL and KEY must be set for Supabase storage")
            self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
    async def save_file(self, file: UploadFile, subfolder: str = "", user_id: str = "") -> str:
        """
        Save uploaded file and return the file URL/path
        
        Args:
            file: FastAPI UploadFile object
            subfolder: Subfolder to organize files (e.g., 'screenshots', 'avatars')
            user_id: User ID for organizing user-specific files
            
        Returns:
            str: URL or path to the saved file
        """
        try:
            # Validate file size
            if file.size and file.size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,  
                    detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
                )
            
            # Generate unique filename
            file_extension = self._get_file_extension(file.filename)
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            if self.storage_type == "local":
                return await self._save_local(file, subfolder, user_id, unique_filename)
            elif self.storage_type == "supabase":
                return await self._save_supabase(file, subfolder, user_id, unique_filename)
            else:
                raise StorageError(f"Unsupported storage type: {self.storage_type}")
                
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file"
            )
    
    async def _save_local(self, file: UploadFile, subfolder: str, user_id: str, filename: str) -> str:
        """Save file to local filesystem"""
        # Create file path
        file_path = self.upload_dir / subfolder
        if user_id:
            file_path = file_path / user_id
        file_path.mkdir(parents=True, exist_ok=True)
        
        full_path = file_path / filename
        
        # Save file
        async with aiofiles.open(full_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Return relative URL path
        relative_path = full_path.relative_to(self.upload_dir)
        return f"/uploads/{relative_path}"
    
    async def _save_supabase(self, file: UploadFile, subfolder: str, user_id: str, filename: str) -> str:
        """Save file to Supabase Storage"""
        try:
            # Create file path
            file_path = subfolder
            if user_id:
                file_path = f"{file_path}/{user_id}" if file_path else user_id
            file_path = f"{file_path}/{filename}" if file_path else filename
            
            # Read file content
            content = await file.read()
            
            # Upload to Supabase
            response = self.supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
                path=file_path,
                file=content,
                file_options={"content-type": file.content_type or "application/octet-stream"}
            )
            
            if response.error:
                raise StorageError(f"Failed to upload to Supabase: {response.error}")
            
            # Return the public URL
            public_url_response = self.supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path)
            return public_url_response
            
        except Exception as e:
            logger.error(f"Error uploading to Supabase: {e}")
            raise StorageError(f"Failed to upload file to Supabase: {e}")
    
    def _get_file_extension(self, filename: Optional[str]) -> str:
        """Extract file extension from filename"""
        if not filename:
            return ""
        return Path(filename).suffix.lower()
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            bool: True if file was deleted successfully
        """
        try:
            if self.storage_type == "local":
                full_path = self.upload_dir / file_path.lstrip("/uploads/")
                if full_path.exists():
                    full_path.unlink()
                    return True
            elif self.storage_type == "supabase":
                # Extract file path from URL if it's a full URL
                if file_path.startswith("http"):
                    # Extract path from Supabase URL
                    path_parts = file_path.split(f"{settings.SUPABASE_BUCKET}/")[-1]
                else:
                    path_parts = file_path.lstrip("/")
                
                response = self.supabase.storage.from_(settings.SUPABASE_BUCKET).remove([path_parts])
                return not response.error
            
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        Get the full URL for a file
        
        Args:
            file_path: Relative file path
            
        Returns:
            str: Full URL to the file
        """
        if file_path.startswith("http"):
            return file_path  # Already a full URL
        
        if self.storage_type == "local":
            return f"{settings.FRONTEND_URL}{file_path}"
        elif self.storage_type == "supabase":
            # If it's already a full URL, return as is
            if file_path.startswith("http"):
                return file_path
            # Otherwise, generate public URL
            return self.supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path.lstrip("/"))
        
        return file_path

# Global storage service instance
storage_service = StorageService()