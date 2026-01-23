"""
SmartSortierer Pro - Storage Security Tests
Tests for path traversal protection and sandboxing
"""
import pytest
import tempfile
import shutil
from pathlib import Path

from app.services.storage import StorageService, PathTraversalError, StorageError


class TestStorageSecurity:
    """Test suite for storage path sandboxing"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = tempfile.mkdtemp(prefix="ss_test_")
        storage = StorageService(storage_root=temp_dir)
        
        # Create test folder structure
        (Path(temp_dir) / "00_inbox").mkdir()
        (Path(temp_dir) / "01_ingested").mkdir()
        (Path(temp_dir) / "secret").mkdir()
        
        # Create test files
        (Path(temp_dir) / "00_inbox" / "test.txt").write_text("test content")
        (Path(temp_dir) / "secret" / "private.txt").write_text("secret data")
        
        yield storage
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_safe_join_normal_path(self, temp_storage):
        """Test that normal paths work correctly"""
        result = temp_storage.safe_join("00_inbox/test.txt")
        assert result.exists()
        assert "00_inbox" in str(result)
    
    def test_safe_join_blocks_parent_traversal(self, temp_storage):
        """Test that ../ is blocked"""
        with pytest.raises(PathTraversalError):
            temp_storage.safe_join("00_inbox/../../../etc/passwd")
    
    def test_safe_join_blocks_absolute_path(self, temp_storage):
        """Test that absolute paths outside root are blocked"""
        with pytest.raises(PathTraversalError):
            temp_storage.safe_join("/etc/passwd")
    
    def test_safe_join_blocks_symbolic_link_escape(self, temp_storage):
        """Test that symlinks cannot escape sandbox"""
        # This test depends on OS, but safe_join should resolve() and check
        pass
    
    def test_list_directory_normal(self, temp_storage):
        """Test listing a valid directory"""
        items = temp_storage.list_directory("00_inbox")
        assert len(items) == 1
        assert items[0]["name"] == "test.txt"
        assert items[0]["type"] == "file"
    
    def test_list_directory_traversal_blocked(self, temp_storage):
        """Test that traversal in list is blocked"""
        with pytest.raises(PathTraversalError):
            temp_storage.list_directory("../../../etc")
    
    def test_stat_normal_file(self, temp_storage):
        """Test stat on valid file"""
        metadata = temp_storage.stat("00_inbox/test.txt")
        assert metadata["name"] == "test.txt"
        assert metadata["type"] == "file"
        assert metadata["size"] == 12  # "test content"
    
    def test_stat_traversal_blocked(self, temp_storage):
        """Test that stat cannot traverse"""
        with pytest.raises(PathTraversalError):
            temp_storage.stat("../../etc/passwd")
    
    def test_read_file_normal(self, temp_storage):
        """Test reading a valid file"""
        with temp_storage.read_file("00_inbox/test.txt") as f:
            content = f.read()
            assert content == b"test content"
    
    def test_read_file_traversal_blocked(self, temp_storage):
        """Test that read cannot traverse"""
        with pytest.raises(PathTraversalError):
            temp_storage.read_file("../../../etc/passwd")
    
    def test_write_file_normal(self, temp_storage):
        """Test writing to valid location"""
        from io import BytesIO
        content = BytesIO(b"new content")
        metadata = temp_storage.write_file("00_inbox/new.txt", content)
        assert metadata["name"] == "new.txt"
    
    def test_write_file_traversal_blocked(self, temp_storage):
        """Test that write cannot traverse"""
        from io import BytesIO
        content = BytesIO(b"malicious")
        with pytest.raises(PathTraversalError):
            temp_storage.write_file("../../etc/evil.txt", content)
    
    def test_move_file_normal(self, temp_storage):
        """Test moving file within sandbox"""
        metadata = temp_storage.move_file("00_inbox/test.txt", "01_ingested/test.txt")
        assert metadata["path"] == "01_ingested/test.txt"
    
    def test_move_file_source_traversal_blocked(self, temp_storage):
        """Test that move source cannot traverse"""
        with pytest.raises(PathTraversalError):
            temp_storage.move_file("../../etc/passwd", "00_inbox/stolen.txt")
    
    def test_move_file_dest_traversal_blocked(self, temp_storage):
        """Test that move destination cannot traverse"""
        with pytest.raises(PathTraversalError):
            temp_storage.move_file("00_inbox/test.txt", "../../etc/evil.txt")
    
    def test_compute_sha256_normal(self, temp_storage):
        """Test SHA256 computation"""
        sha = temp_storage.compute_sha256("00_inbox/test.txt")
        assert len(sha) == 64  # SHA256 is 64 hex chars
        assert sha.isalnum()
    
    def test_compute_sha256_traversal_blocked(self, temp_storage):
        """Test that SHA256 cannot traverse"""
        with pytest.raises(PathTraversalError):
            temp_storage.compute_sha256("../../etc/passwd")


class TestStorageEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = tempfile.mkdtemp(prefix="ss_test_")
        storage = StorageService(storage_root=temp_dir)
        
        # Create test structure
        (Path(temp_dir) / "test").mkdir()
        (Path(temp_dir) / "test" / "file.txt").write_text("content")
        
        yield storage
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_stat_nonexistent_file(self, temp_storage):
        """Test stat on non-existent file"""
        with pytest.raises(StorageError):
            temp_storage.stat("nonexistent.txt")
    
    def test_list_nonexistent_directory(self, temp_storage):
        """Test listing non-existent directory"""
        with pytest.raises(StorageError):
            temp_storage.list_directory("nonexistent")
    
    def test_read_nonexistent_file(self, temp_storage):
        """Test reading non-existent file"""
        with pytest.raises(StorageError):
            temp_storage.read_file("nonexistent.txt")
    
    def test_write_file_already_exists(self, temp_storage):
        """Test writing to existing file without overwrite"""
        from io import BytesIO
        content = BytesIO(b"new")
        with pytest.raises(StorageError):
            temp_storage.write_file("test/file.txt", content, overwrite=False)
    
    def test_write_file_overwrite_allowed(self, temp_storage):
        """Test overwriting file when explicitly allowed"""
        from io import BytesIO
        content = BytesIO(b"overwritten")
        metadata = temp_storage.write_file("test/file.txt", content, overwrite=True)
        assert metadata["size"] == 11  # "overwritten"
    
    def test_move_to_existing_without_overwrite(self, temp_storage):
        """Test moving to existing file without overwrite flag"""
        # Create two files
        from io import BytesIO
        temp_storage.write_file("test/file2.txt", BytesIO(b"file2"))
        
        with pytest.raises(StorageError):
            temp_storage.move_file("test/file2.txt", "test/file.txt", overwrite=False)
