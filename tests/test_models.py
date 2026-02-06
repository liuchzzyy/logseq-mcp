"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from models.enums import PageFormat
from models.schemas import (
    CreatePageInput,
    DeleteBlockInput,
    DeletePageInput,
    EditBlockInput,
    EmptyInput,
    GetAllPagesInput,
    GetBlockInput,
    GetPageInput,
    GetTasksInput,
    InsertBlockInput,
    MoveBlockInput,
    RenamePageInput,
    SimpleQueryInput,
    UpdateBlockInput,
)


class TestInsertBlockInput:
    """Test InsertBlockInput model."""

    def test_valid_input(self):
        """Test valid insert block input."""
        data = {
            "parent_block": "test-uuid",
            "content": "Test content",
            "is_page_block": False,
            "before": True,
        }
        model = InsertBlockInput(**data)
        assert model.parent_block == "test-uuid"
        assert model.content == "Test content"
        assert model.is_page_block is False
        assert model.before is True

    def test_content_required(self):
        """Test that content is required."""
        with pytest.raises(ValidationError) as exc_info:
            InsertBlockInput()
        assert "content" in str(exc_info.value)

    def test_block_ref_cleaning(self):
        """Test that ((uuid)) format is cleaned."""
        model = InsertBlockInput(parent_block="((test-uuid))", content="test")
        assert model.parent_block == "test-uuid"

    def test_custom_uuid_cleaning(self):
        """Test that custom UUID is cleaned."""
        model = InsertBlockInput(content="test", custom_uuid="((custom-uuid))")
        assert model.custom_uuid == "custom-uuid"

    def test_optional_fields_defaults(self):
        """Test default values for optional fields."""
        model = InsertBlockInput(content="test")
        assert model.parent_block is None
        assert model.is_page_block is False
        assert model.before is False
        assert model.custom_uuid is None
        assert model.properties is None

    def test_properties_validation(self):
        """Test properties field validation."""
        props = {"tags": ["test"], "status": "active"}
        model = InsertBlockInput(content="test", properties=props)
        assert model.properties == props


class TestUpdateBlockInput:
    """Test UpdateBlockInput model."""

    def test_valid_input(self):
        """Test valid update block input."""
        data = {"uuid": "test-uuid", "content": "Updated content"}
        model = UpdateBlockInput(**data)
        assert model.uuid == "test-uuid"
        assert model.content == "Updated content"

    def test_required_fields(self):
        """Test that uuid and content are required."""
        with pytest.raises(ValidationError):
            UpdateBlockInput(uuid="test")

        with pytest.raises(ValidationError):
            UpdateBlockInput(content="test")

    def test_optional_properties(self):
        """Test optional properties field."""
        model = UpdateBlockInput(uuid="test", content="test", properties={"key": "value"})
        assert model.properties == {"key": "value"}


class TestMoveBlockInput:
    """Test MoveBlockInput model."""

    def test_valid_input(self):
        """Test valid move block input."""
        data = {
            "uuid": "source-uuid",
            "target_uuid": "target-uuid",
            "as_child": True,
        }
        model = MoveBlockInput(**data)
        assert model.uuid == "source-uuid"
        assert model.target_uuid == "target-uuid"
        assert model.as_child is True

    def test_default_as_child(self):
        """Test default value for as_child."""
        model = MoveBlockInput(uuid="source", target_uuid="target")
        assert model.as_child is False

    def test_required_fields(self):
        """Test that both uuids are required."""
        with pytest.raises(ValidationError):
            MoveBlockInput(uuid="source")

        with pytest.raises(ValidationError):
            MoveBlockInput(target_uuid="target")


class TestDeleteBlockInput:
    """Test DeleteBlockInput model."""

    def test_valid_input(self):
        """Test valid delete block input."""
        model = DeleteBlockInput(uuid="test-uuid")
        assert model.uuid == "test-uuid"

    def test_uuid_required(self):
        """Test that uuid is required."""
        with pytest.raises(ValidationError):
            DeleteBlockInput()


class TestGetBlockInput:
    """Test GetBlockInput model."""

    def test_valid_input(self):
        """Test valid get block input."""
        model = GetBlockInput(uuid="test-uuid")
        assert model.uuid == "test-uuid"

    def test_uuid_required(self):
        """Test that uuid is required."""
        with pytest.raises(ValidationError):
            GetBlockInput()


class TestCreatePageInput:
    """Test CreatePageInput model."""

    def test_valid_input(self):
        """Test valid create page input."""
        data = {
            "page_name": "Test Page",
            "properties": {"tags": ["test"]},
            "journal": False,
            "format": PageFormat.MARKDOWN,
            "create_first_block": True,
        }
        model = CreatePageInput(**data)
        assert model.page_name == "Test Page"
        assert model.properties == {"tags": ["test"]}
        assert model.journal is False
        assert model.format == PageFormat.MARKDOWN
        assert model.create_first_block is True

    def test_page_name_required(self):
        """Test that page_name is required."""
        with pytest.raises(ValidationError):
            CreatePageInput()

    def test_default_values(self):
        """Test default values."""
        model = CreatePageInput(page_name="Test")
        # Properties is None by default, service layer handles the default
        assert model.properties is None
        assert model.journal is False
        assert model.format == PageFormat.MARKDOWN
        assert model.create_first_block is True

    def test_properties_json_parsing(self):
        """Test that properties can be parsed from JSON string."""
        model = CreatePageInput(page_name="Test", properties='{"key": "value"}')
        assert model.properties == {"key": "value"}

    def test_invalid_properties_json(self):
        """Test that invalid JSON raises error."""
        with pytest.raises(ValidationError) as exc_info:
            CreatePageInput(page_name="Test", properties="invalid json")
        assert "Invalid JSON" in str(exc_info.value)

    def test_org_format(self):
        """Test org format page creation."""
        model = CreatePageInput(page_name="Test", format=PageFormat.ORG)
        assert model.format == PageFormat.ORG


class TestGetPageInput:
    """Test GetPageInput model."""

    def test_valid_input(self):
        """Test valid get page input."""
        data = {"src_page": "Test Page", "include_children": True}
        model = GetPageInput(**data)
        assert model.src_page == "Test Page"
        assert model.include_children is True

    def test_src_page_required(self):
        """Test that src_page is required."""
        with pytest.raises(ValidationError):
            GetPageInput()

    def test_default_include_children(self):
        """Test default value for include_children."""
        model = GetPageInput(src_page="Test")
        assert model.include_children is False


class TestDeletePageInput:
    """Test DeletePageInput model."""

    def test_valid_input(self):
        """Test valid delete page input."""
        model = DeletePageInput(page_name="Test Page")
        assert model.page_name == "Test Page"

    def test_page_name_required(self):
        """Test that page_name is required."""
        with pytest.raises(ValidationError):
            DeletePageInput()


class TestRenamePageInput:
    """Test RenamePageInput model."""

    def test_valid_input(self):
        """Test valid rename page input."""
        data = {"old_name": "Old Page", "new_name": "New Page"}
        model = RenamePageInput(**data)
        assert model.old_name == "Old Page"
        assert model.new_name == "New Page"

    def test_both_names_required(self):
        """Test that both old and new names are required."""
        with pytest.raises(ValidationError):
            RenamePageInput(old_name="Old")

        with pytest.raises(ValidationError):
            RenamePageInput(new_name="New")


class TestGetAllPagesInput:
    """Test GetAllPagesInput model."""

    def test_valid_with_repo(self):
        """Test with repository specified."""
        model = GetAllPagesInput(repo="my-repo")
        assert model.repo == "my-repo"

    def test_valid_without_repo(self):
        """Test without repository (optional)."""
        model = GetAllPagesInput()
        assert model.repo is None


class TestEditBlockInput:
    """Test EditBlockInput model."""

    def test_valid_input(self):
        """Test valid edit block input."""
        data = {"src_block": "block-uuid", "pos": 10}
        model = EditBlockInput(**data)
        assert model.src_block == "block-uuid"
        assert model.pos == 10

    def test_src_block_required(self):
        """Test that src_block is required."""
        with pytest.raises(ValidationError):
            EditBlockInput()

    def test_default_pos(self):
        """Test default position value."""
        model = EditBlockInput(src_block="test")
        assert model.pos == 0

    def test_pos_bounds(self):
        """Test position bounds validation."""
        with pytest.raises(ValidationError):
            EditBlockInput(src_block="test", pos=-1)

        with pytest.raises(ValidationError):
            EditBlockInput(src_block="test", pos=10001)


class TestEmptyInput:
    """Test EmptyInput model."""

    def test_empty_input(self):
        """Test empty input creation."""
        model = EmptyInput()
        assert model is not None


class TestSimpleQueryInput:
    """Test SimpleQueryInput model."""

    def test_valid_input(self):
        """Test valid simple query input."""
        model = SimpleQueryInput(query="[[Project]]")
        assert model.query == "[[Project]]"

    def test_query_required(self):
        """Test that query is required."""
        with pytest.raises(ValidationError):
            SimpleQueryInput()


class TestGetTasksInput:
    """Test GetTasksInput model."""

    def test_valid_with_filters(self):
        """Test with all filters."""
        model = GetTasksInput(marker="TODO", priority="A")
        assert model.marker == "TODO"
        assert model.priority == "A"

    def test_valid_without_filters(self):
        """Test without filters."""
        model = GetTasksInput()
        assert model.marker is None
        assert model.priority is None

    def test_partial_filters(self):
        """Test with partial filters."""
        model = GetTasksInput(marker="DONE")
        assert model.marker == "DONE"
        assert model.priority is None
